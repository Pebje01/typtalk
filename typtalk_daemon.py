#!/usr/bin/env python3
"""
TypTalk Daemon - Spraak naar tekst zonder pynput
Luistert naar commando's via FIFO pipe
"""

import json
import os
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
from pynput.keyboard import Controller, Key

import config


class TypTalkDaemon:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.keyboard_controller = Controller()
        self.whisper_model = None
        self.typing_lock = threading.Lock()
        self.processing = False
        self.stream = None

        # Control pipe
        self.pipe_path = Path.home() / ".typtalk_control"

        # Rate limiting
        self.request_times = []
        self.last_request_time = 0
        self.recording_start_time = 0

        # Kosten tracking
        self.cost_file = Path(config.COST_FILE).expanduser()
        self.monthly_cost = self._load_costs()
        self.budget_warning_shown = False

        self._log("TypTalk Daemon initialiseren...")
        self._load_whisper_model()
        self._setup_pipe()
        self._log("Daemon gereed! Wacht op commando's...")

    def _log(self, message: str):
        """Print debug berichten indien ingeschakeld."""
        if config.DEBUG:
            print(f"[TypTalk Daemon] {message}", flush=True)

    def _setup_pipe(self):
        """Maak FIFO pipe voor commando's."""
        if self.pipe_path.exists():
            self.pipe_path.unlink()
        os.mkfifo(str(self.pipe_path))
        self._log(f"Control pipe: {self.pipe_path}")

    def _load_costs(self) -> float:
        """Laad maandelijkse kosten uit bestand."""
        try:
            if self.cost_file.exists():
                data = json.loads(self.cost_file.read_text())
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

    def _add_cost(self, audio_seconds: float):
        """Voeg kosten toe voor OpenAI Whisper API."""
        cost_per_minute = 0.006 * 0.92  # €0.00552 per minuut
        cost = (audio_seconds / 60) * cost_per_minute
        self.monthly_cost += cost
        self._save_costs()

    def _check_budget(self) -> bool:
        """Check of we binnen budget zijn."""
        if self.monthly_cost >= config.BUDGET_LIMIT:
            self._log("Budget limiet bereikt, API overgeslagen.")
            return False
        return True

    def _load_whisper_model(self):
        """Laad het Whisper model."""
        self._log(f"Whisper model '{config.WHISPER_MODEL}' laden...")
        self.whisper_model = whisper.load_model(config.WHISPER_MODEL)
        self._log("Whisper model geladen.")

    def start_recording(self):
        """Start audio opname."""
        # Debounce: voorkom te snelle start commando's
        now = time.time()
        if hasattr(self, 'last_stop_time'):
            if now - self.last_stop_time < 0.5:  # Min 0.5 sec tussen opnames
                self._log("⏭️  Te snel, genegeerd (debounce)")
                return

        if self.recording or self.processing:
            self._log("Al aan het opnemen of verwerken...")
            return

        self.recording = True
        self.audio_data = []
        self.recording_start_time = time.time()
        self._log("🎤 Opname gestart...")

        def audio_callback(indata, frames, time_info, status):
            if status:
                self._log(f"Audio status: {status}")
            if self.recording:
                self.audio_data.append(indata.copy())
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

    def stop_recording(self):
        """Stop opname en verwerk audio."""
        if not self.recording:
            return

        # Check minimale opnametijd (voorkom accidentele tap)
        elapsed = time.time() - self.recording_start_time
        if elapsed < 0.3:  # Minder dan 0.3 sec = waarschijnlijk per ongeluk
            self._log("⏭️  Te kort (accidentele tap), genegeerd")
            self.recording = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.audio_data = []
            return

        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self._log("⏹️  Opname gestopt.")
        self.last_stop_time = time.time()

        if not self.audio_data:
            self._log("Geen audio opgenomen.")
            return

        # Combineer audio chunks
        audio = np.concatenate(self.audio_data, axis=0)
        duration = len(audio) / config.SAMPLE_RATE
        self._log(f"Audio: {duration:.1f} seconden")

        if duration < 0.5:
            self._log("Opname te kort, genegeerd.")
            return

        # Verwerk in aparte thread
        thread = threading.Thread(target=self._process_audio, args=(audio,))
        thread.start()

    def _save_audio_to_temp(self, audio: np.ndarray) -> str:
        """Sla audio op als tijdelijk WAV bestand."""
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = temp_file.name
        temp_file.close()

        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(config.CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(config.SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        return temp_path

    def _transcribe(self, audio_path: str) -> str:
        """Transcribeer audio met Whisper."""
        if config.OPENAI_WHISPER_ENABLED and config.OPENAI_API_KEY:
            return self._transcribe_openai(audio_path)
        else:
            return self._transcribe_local(audio_path)

    def _transcribe_local(self, audio_path: str) -> str:
        """Transcribeer audio met lokale Whisper."""
        self._log("Transcriberen (lokaal)...")
        result = self.whisper_model.transcribe(
            audio_path,
            language=config.WHISPER_LANGUAGE,
            initial_prompt=config.WHISPER_PROMPT,
            fp16=False
        )
        text = result["text"].strip()
        self._log(f"Transcriptie: {text}")
        return text

    def _transcribe_openai(self, audio_path: str) -> str:
        """Transcribeer audio met OpenAI Whisper API."""
        self._log("Transcriberen (OpenAI)...")
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
            self._log(f"OpenAI fout: {e}, fallback naar lokaal...")
            return self._transcribe_local(audio_path)

    def _type_text(self, text: str):
        """Typ tekst via clipboard."""
        if not text:
            return

        with self.typing_lock:
            self._log(f"✍️  Typen: {text}")
            import subprocess
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            self.keyboard_controller.press(Key.cmd)
            self.keyboard_controller.tap('v')
            self.keyboard_controller.release(Key.cmd)

    def _process_audio(self, audio: np.ndarray):
        """Verwerk audio in aparte thread."""
        if self.processing:
            return

        self.processing = True
        try:
            duration = len(audio) / config.SAMPLE_RATE
            audio_path = self._save_audio_to_temp(audio)

            text = self._transcribe(audio_path)
            Path(audio_path).unlink(missing_ok=True)

            if text:
                self._add_cost(duration)
                self._type_text(text)
        except Exception as e:
            self._log(f"FOUT: {e}")
        finally:
            self.processing = False

    def run(self):
        """Luister naar commando's op de pipe."""
        print("=" * 50)
        print("TypTalk Daemon - Geen permissies nodig!")
        print("=" * 50)
        print(f"Control pipe: {self.pipe_path}")
        print("Wacht op Fn-toets via Karabiner...")
        print("=" * 50)

        try:
            while True:
                # Open pipe (blocks until someone writes)
                with open(self.pipe_path, 'r') as pipe:
                    command = pipe.read().strip()

                    if command == "start":
                        self.start_recording()
                    elif command == "stop":
                        self.stop_recording()
                    elif command == "quit":
                        self._log("Shutdown ontvangen")
                        break
                    else:
                        self._log(f"Onbekend commando: {command}")
        except KeyboardInterrupt:
            print("\nGestopt.")
        finally:
            if self.pipe_path.exists():
                self.pipe_path.unlink()


def main():
    """Hoofdfunctie."""
    daemon = TypTalkDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
