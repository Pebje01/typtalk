#!/usr/bin/env python3
"""
Wispr Flow Clone - Spraak naar tekst met AI verbetering

Gebruik:
1. Start het script: python wispr.py
2. Houd de hotkey ingedrukt en spreek
3. Laat de hotkey los
4. De verbeterde tekst wordt automatisch getypt
"""

import json
import tempfile
import threading
import time
import wave
from datetime import datetime
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd
import whisper
from pynput import keyboard
from pynput.keyboard import Controller, Key

import config


class WisprClone:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.keyboard_controller = Controller()
        self.whisper_model = None
        self.hotkey = self._parse_hotkey(config.HOTKEY)
        self.typing_lock = threading.Lock()
        self.processing = False

        # Rate limiting
        self.request_times = []
        self.last_request_time = 0
        self.recording_start_time = 0

        # Kosten tracking
        self.cost_file = Path(config.COST_FILE).expanduser()
        self.monthly_cost = self._load_costs()
        self.budget_warning_shown = False

        self._log("Wispr Clone initialiseren...")
        self._load_whisper_model()
        self._log(f"Hotkey: {config.HOTKEY}")
        self._log("Gereed! Houd de hotkey ingedrukt om te spreken.")

    def _log(self, message: str):
        """Print debug berichten indien ingeschakeld."""
        if config.DEBUG:
            print(f"[Wispr] {message}", flush=True)

    def _notify(self, title: str, message: str):
        """Toon macOS popup."""
        import subprocess
        subprocess.run([
            "osascript", "-e",
            f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"'
        ], capture_output=True)

    def _check_rate_limit(self) -> bool:
        """Check of we binnen de rate limit zijn. Returns True als OK."""
        now = time.time()

        # Check cooldown
        if now - self.last_request_time < config.REQUEST_COOLDOWN:
            self._log("Rate limit: cooldown actief, even wachten...")
            return False

        # Verwijder oude timestamps (ouder dan 60 sec)
        self.request_times = [t for t in self.request_times if now - t < 60]

        # Check max per minuut
        if len(self.request_times) >= config.MAX_REQUESTS_PER_MINUTE:
            self._log("Rate limit: max requests per minuut bereikt!")
            return False

        return True

    def _register_request(self):
        """Registreer een API request."""
        now = time.time()
        self.request_times.append(now)
        self.last_request_time = now

    def _load_costs(self) -> float:
        """Laad maandelijkse kosten uit bestand."""
        try:
            if self.cost_file.exists():
                data = json.loads(self.cost_file.read_text())
                # Reset als nieuwe maand
                if data.get("month") != datetime.now().strftime("%Y-%m"):
                    return 0.0
                return data.get("cost", 0.0)
        except Exception:
            pass
        return 0.0

    def _save_costs(self):
        """Sla kosten op naar bestand."""
        try:
            data = {
                "month": datetime.now().strftime("%Y-%m"),
                "cost": self.monthly_cost
            }
            self.cost_file.write_text(json.dumps(data))
        except Exception as e:
            self._log(f"Kon kosten niet opslaan: {e}")

    def _add_cost(self, tokens: int):
        """Voeg kosten toe (Gemini Flash pricing)."""
        # Gemini Flash: $0.075/1M input + $0.30/1M output ≈ $0.40/1M tokens totaal
        # Omgerekend naar euro (€0.92 per $1)
        cost_per_token = 0.0000004 * 0.92  # €0.00000037 per token
        cost = tokens * cost_per_token
        self.monthly_cost += cost
        self._save_costs()

        # Waarschuwingen
        if self.monthly_cost >= config.BUDGET_LIMIT:
            self._log(f"BUDGET LIMIET BEREIKT! €{self.monthly_cost:.2f} deze maand. API uitgeschakeld.")
            self._notify("Wispr Clone - Budget Op!", f"€{self.monthly_cost:.2f} bereikt. Transcriptie gestopt.")
        elif self.monthly_cost >= config.BUDGET_WARNING and not self.budget_warning_shown:
            self._log(f"WAARSCHUWING: €{self.monthly_cost:.2f} deze maand (limiet: €{config.BUDGET_LIMIT})")
            self._notify("Wispr Clone - Budget Waarschuwing", f"€{self.monthly_cost:.2f} van €{config.BUDGET_LIMIT} gebruikt.")
            self.budget_warning_shown = True

    def _check_budget(self) -> bool:
        """Check of we binnen budget zijn."""
        if self.monthly_cost >= config.BUDGET_LIMIT:
            self._log("Budget limiet bereikt, API overgeslagen.")
            return False
        return True

    def _get_hotkey_from_file(self) -> str | None:
        """Lees hotkey uit bestand indien aanwezig."""
        hotkey_file = Path("~/.wispr_hotkey.json").expanduser()
        try:
            if hotkey_file.exists():
                data = json.loads(hotkey_file.read_text())
                return data.get("hotkey")
        except Exception:
            pass
        return None

    def _parse_hotkey(self, hotkey_str: str):
        """Parse hotkey string naar pynput Key object."""
        # Check eerst of er een hotkey bestand is
        file_hotkey = self._get_hotkey_from_file()
        if file_hotkey:
            hotkey_str = file_hotkey
            self._log(f"Hotkey uit bestand: {hotkey_str}")

        hotkey_map = {
            "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
            "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
            "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
            "f13": Key.f13, "f14": Key.f14, "f15": Key.f15, "f16": Key.f16,
            "f17": Key.f17, "f18": Key.f18, "f19": Key.f19, "f20": Key.f20,
            "alt_r": Key.alt_r, "alt_l": Key.alt_l,
            "ctrl_r": Key.ctrl_r, "ctrl_l": Key.ctrl_l,
            "cmd_r": Key.cmd_r, "cmd_l": Key.cmd_l,
            "caps_lock": Key.caps_lock,
            "shift_r": Key.shift_r, "shift_l": Key.shift_l,
        }
        return hotkey_map.get(hotkey_str.lower(), Key.alt_r)

    def _load_whisper_model(self):
        """Laad het Whisper model."""
        self._log(f"Whisper model '{config.WHISPER_MODEL}' laden...")
        self.whisper_model = whisper.load_model(config.WHISPER_MODEL)
        self._log("Whisper model geladen.")

    def _start_recording(self):
        """Start audio opname."""
        if self.recording or self.processing:
            return

        self.recording = True
        self.audio_data = []
        self.recording_start_time = time.time()
        self._log("Opname gestart... Spreek nu.")

        def audio_callback(indata, frames, time_info, status):
            if status:
                self._log(f"Audio status: {status}")
            if self.recording:
                self.audio_data.append(indata.copy())
                # Auto-stop na 30 seconden
                if time.time() - self.recording_start_time > 30:
                    self._log("Auto-stop: max 30 seconden bereikt")
                    self.recording = False

        self.stream = sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            channels=config.CHANNELS,
            dtype=np.float32,
            callback=audio_callback
        )
        self.stream.start()

    def _stop_recording(self) -> np.ndarray | None:
        """Stop opname en retourneer audio data."""
        if not self.recording:
            return None

        self.recording = False
        self.stream.stop()
        self.stream.close()
        self._log("Opname gestopt.")

        if not self.audio_data:
            self._log("Geen audio opgenomen.")
            return None

        # Combineer alle audio chunks
        audio = np.concatenate(self.audio_data, axis=0)
        self._log(f"Audio opgenomen: {len(audio) / config.SAMPLE_RATE:.1f} seconden")
        return audio

    def _save_audio_to_temp(self, audio: np.ndarray) -> str:
        """Sla audio op als tijdelijk WAV bestand."""
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = temp_file.name
        temp_file.close()

        # Converteer naar 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(config.CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(config.SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        return temp_path

    def _transcribe(self, audio_path: str) -> str:
        """Transcribeer audio met Whisper (lokaal of cloud)."""
        if config.OPENAI_WHISPER_ENABLED and config.OPENAI_API_KEY:
            return self._transcribe_openai(audio_path)
        else:
            return self._transcribe_local(audio_path)

    def _transcribe_local(self, audio_path: str) -> str:
        """Transcribeer audio met lokale Whisper."""
        self._log("Transcriberen met Whisper (lokaal)...")

        result = self.whisper_model.transcribe(
            audio_path,
            language=config.WHISPER_LANGUAGE,
            initial_prompt=config.WHISPER_PROMPT,
            fp16=False  # CPU compatibiliteit
        )

        text = result["text"].strip()
        self._log(f"Transcriptie: {text}")
        return text

    def _transcribe_openai(self, audio_path: str) -> str:
        """Transcribeer audio met OpenAI Whisper API (sneller)."""
        self._log("Transcriberen met Whisper (cloud)...")

        try:
            with open(audio_path, "rb") as audio_file:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
                    files={"file": ("audio.wav", audio_file, "audio/wav")},
                    data={
                        "model": "whisper-1",
                        "language": config.WHISPER_LANGUAGE,
                        "prompt": config.WHISPER_PROMPT
                    },
                    timeout=30
                )
            response.raise_for_status()
            text = response.json().get("text", "").strip()
            self._log(f"Transcriptie: {text}")
            return text

        except Exception as e:
            self._log(f"OpenAI Whisper fout: {e}, fallback naar lokaal...")
            return self._transcribe_local(audio_path)

    def _improve_with_ollama(self, text: str) -> str:
        """Verbeter tekst met Ollama."""
        if not text:
            return text

        # Rate limit check
        if not self._check_rate_limit():
            return text

        self._log("Verbeteren met Ollama...")
        self._register_request()

        try:
            response = requests.post(
                config.OLLAMA_URL,
                json={
                    "model": config.OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": config.OLLAMA_SYSTEM},
                        {"role": "user", "content": text}
                    ],
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            improved_text = result.get("message", {}).get("content", text).strip()

            # Pak alleen de eerste regel (voorkomt dat LLM gaat "praten")
            first_line = improved_text.split('\n')[0].strip()

            # Als de output veel langer is dan de input, gebruik dan de input
            if len(first_line) > len(text) * 2:
                self._log("Ollama output te lang, origineel gebruikt.")
                return text

            self._log(f"Verbeterd: {first_line}")
            return first_line

        except requests.exceptions.ConnectionError:
            self._log("WAARSCHUWING: Ollama niet bereikbaar. Originele tekst wordt gebruikt.")
            return text
        except requests.exceptions.Timeout:
            self._log("WAARSCHUWING: Ollama timeout. Originele tekst wordt gebruikt.")
            return text
        except Exception as e:
            self._log(f"WAARSCHUWING: Ollama fout: {e}. Originele tekst wordt gebruikt.")
            return text

    def _improve_with_gemini(self, text: str) -> str:
        """Verbeter tekst met Gemini API."""
        if not text:
            return text

        if not config.GEMINI_API_KEY:
            self._log("Geen Gemini API key geconfigureerd.")
            return text

        # Rate limit en budget check
        if not self._check_rate_limit() or not self._check_budget():
            return text

        self._log("Verbeteren met Gemini...")
        self._register_request()

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"

            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Fix spelfouten en zet interpunctie goed (punten, komma's). Behoud de woorden. Geef alleen de tekst terug:\n\n{text}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 500
                }
            }

            # Probeer max 2 keer met retry bij rate limit
            for attempt in range(2):
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 429 and attempt == 0:
                    self._log("Rate limit, 2 sec wachten...")
                    time.sleep(2)
                    continue
                break
            response.raise_for_status()

            result = response.json()
            improved_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

            # Kosten bijhouden (schatting: input + output tokens)
            total_tokens = len(text.split()) + len(improved_text.split())
            self._add_cost(total_tokens * 2)  # ~2 tokens per woord

            # Pak alleen eerste regel
            first_line = improved_text.split('\n')[0].strip()

            if len(first_line) > len(text) * 2:
                self._log("Gemini output te lang, origineel gebruikt.")
                return text

            self._log(f"Verbeterd: {first_line}")
            return first_line

        except Exception as e:
            self._log(f"WAARSCHUWING: Gemini fout: {e}. Originele tekst wordt gebruikt.")
            return text

    def _type_text(self, text: str):
        """Typ tekst waar de cursor staat (via clipboard voor snelheid)."""
        if not text:
            return

        with self.typing_lock:
            self._log(f"Typen: {text}")
            import subprocess
            # Kopieer naar clipboard
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            # Plak met Cmd+V
            self.keyboard_controller.press(Key.cmd)
            self.keyboard_controller.tap('v')
            self.keyboard_controller.release(Key.cmd)

    def _process_audio(self, audio: np.ndarray):
        """Verwerk audio in een aparte thread."""
        if self.processing:
            self._log("Nog bezig met vorige opname, even wachten...")
            return

        # Minimum opnametijd (voorkomt hallucinaties bij te korte audio)
        duration = len(audio) / config.SAMPLE_RATE
        if duration < 0.5:
            self._log(f"Opname te kort ({duration:.1f}s), genegeerd.")
            return

        self.processing = True
        try:
            start_total = time.time()

            # Sla audio op
            audio_path = self._save_audio_to_temp(audio)

            # Transcribeer
            t1 = time.time()
            text = self._transcribe(audio_path)
            self._log(f"[TIMING] Whisper: {time.time() - t1:.1f}s")

            # Verwijder temp bestand
            Path(audio_path).unlink(missing_ok=True)

            if not text:
                self._log("Geen tekst gedetecteerd.")
                return

            # Verbeter met Gemini of Ollama indien ingeschakeld
            t2 = time.time()
            if config.GEMINI_ENABLED and len(text.split()) >= 3:
                improved_text = self._improve_with_gemini(text)
                self._log(f"[TIMING] Gemini: {time.time() - t2:.1f}s")
            elif config.OLLAMA_ENABLED and len(text.split()) >= 3:
                improved_text = self._improve_with_ollama(text)
                self._log(f"[TIMING] Ollama: {time.time() - t2:.1f}s")
            else:
                improved_text = text

            # Typ de tekst
            self._type_text(improved_text)

            self._log(f"[TIMING] Totaal: {time.time() - start_total:.1f}s")

        except Exception as e:
            self._log(f"FOUT: {e}")
        finally:
            self.processing = False

    def _on_press(self, key):
        """Callback voor toets indrukken."""
        if key == self.hotkey:
            self._start_recording()

    def _on_release(self, key):
        """Callback voor toets loslaten."""
        if key == self.hotkey:
            audio = self._stop_recording()
            if audio is not None:
                # Verwerk in aparte thread om UI niet te blokkeren
                thread = threading.Thread(target=self._process_audio, args=(audio,))
                thread.start()

    def run(self):
        """Start de hotkey listener."""
        # Bepaal welke hotkey actief is
        hotkey_name = self._get_hotkey_from_file() or config.HOTKEY
        whisper_mode = "cloud (OpenAI)" if config.OPENAI_WHISPER_ENABLED else "lokaal"

        print("=" * 50)
        print("Wispr Flow Clone")
        print("=" * 50)
        print(f"Hotkey: {hotkey_name}")
        print(f"Whisper: {whisper_mode}")
        print("=" * 50)
        print("Houd de hotkey ingedrukt om te spreken.")
        print("Druk Ctrl+C om te stoppen.")
        print("=" * 50)

        with keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        ) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                print("\nGestopt.")


def check_dependencies():
    """Controleer of alle dependencies beschikbaar zijn."""
    errors = []

    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            errors.append("Ollama draait niet. Start met: ollama serve")
    except requests.exceptions.ConnectionError:
        errors.append("Ollama niet bereikbaar. Installeer en start Ollama:")
        errors.append("  brew install ollama")
        errors.append("  ollama serve")
        errors.append(f"  ollama pull {config.OLLAMA_MODEL}")

    # Check audio devices
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if not input_devices:
            errors.append("Geen audio input device gevonden.")
    except Exception as e:
        errors.append(f"Audio device fout: {e}")

    return errors


def main():
    """Hoofdfunctie."""
    print("Checking dependencies...", flush=True)

    errors = check_dependencies()
    if errors:
        print("\n⚠️  Waarschuwingen:")
        for error in errors:
            print(f"  - {error}")
        print("\nHet script zal proberen te draaien, maar sommige functies werken mogelijk niet.\n")

    wispr = WisprClone()
    wispr.run()


if __name__ == "__main__":
    main()
