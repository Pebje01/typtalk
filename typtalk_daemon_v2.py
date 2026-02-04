#!/usr/bin/env python3
"""
TypTalk Daemon V2 - Signal-based (STABIEL)
Gebruikt Unix signals in plaats van FIFO pipe
"""

import json
import os
import signal
import sys
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

        # Rate limiting
        self.request_times = []
        self.last_request_time = 0
        self.recording_start_time = 0
        self.last_stop_time = 0

        # Kosten tracking
        self.cost_file = Path(config.COST_FILE).expanduser()
        self.monthly_cost = self._load_costs()
        self.budget_warning_shown = False

        # PID file voor signal communication
        self.pid_file = Path.home() / ".typtalk_pid"

        self._log("TypTalk Daemon V2 (Signal-based) initialiseren...")
        self._load_whisper_model()
        self._setup_signals()
        self._save_pid()
        self._log("Daemon gereed! Wacht op Fn-toets...")

    def _log(self, message: str):
        """Print debug berichten indien ingeschakeld."""
        if config.DEBUG:
            print(f"[TypTalk V2] {message}", flush=True)

    def _setup_signals(self):
        """Setup signal handlers voor start/stop."""
        signal.signal(signal.SIGUSR1, self._signal_start)
        signal.signal(signal.SIGUSR2, self._signal_stop)
        signal.signal(signal.SIGTERM, self._signal_quit)
        signal.signal(signal.SIGINT, self._signal_quit)
        self._log("Signal handlers geregistreerd (SIGUSR1=start, SIGUSR2=stop)")

    def _save_pid(self):
        """Sla process ID op voor signal communication."""
        self.pid_file.write_text(str(os.getpid()))
        self._log(f"PID {os.getpid()} opgeslagen")

    def _signal_start(self, signum, frame):
        """Signal handler: start recording."""
        self.start_recording()

    def _signal_stop(self, signum, frame):
        """Signal handler: stop recording."""
        self.stop_recording()

    def _signal_quit(self, signum, frame):
        """Signal handler: graceful shutdown."""
        self._log("Shutdown signal ontvangen")
        if self.pid_file.exists():
            self.pid_file.unlink()
        sys.exit(0)

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
        cost_per_minute = 0.006 * 0.92
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
        # Debounce
        now = time.time()
        if hasattr(self, 'last_stop_time') and self.last_stop_time > 0:
            if now - self.last_stop_time < 0.8:
                self._log("⏭️  Debounce: te snel")
                return

        if self.recording or self.processing:
            self._log("⚠️  Al bezig, genegeerd")
            return

        self.recording = True
        self.audio_data = []
        self.recording_start_time = time.time()
        self._log("🎤 START")

        def audio_callback(indata, frames, time_info, status):
            if status:
                self._log(f"Audio: {status}")
            if self.recording:
                self.audio_data.append(indata.copy())
                if time.time() - self.recording_start_time > 20:
                    self._log("⏰ Auto-stop: 20 sec")
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
            self._log("⚠️  Stop ignored: niet aan het opnemen")
            return

        elapsed = time.time() - self.recording_start_time

        # Te kort (verhoogd naar 1 sec om hallucinations te voorkomen)
        if elapsed < 1.0:
            self._log(f"⏭️  Te kort ({elapsed:.1f}s) - voorkomt hallucinations")
            self.recording = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.audio_data = []
            self.last_stop_time = time.time()
            return

        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()

        self._log(f"⏹️  STOP ({elapsed:.1f}s)")
        self.last_stop_time = time.time()

        if not self.audio_data:
            self._log("Geen audio")
            return

        # Combineer en verwerk
        audio = np.concatenate(self.audio_data, axis=0)
        thread = threading.Thread(target=self._process_audio, args=(audio,))
        thread.daemon = True
        thread.start()

    def _save_audio_to_temp(self, audio: np.ndarray) -> str:
        """Sla audio op als WAV."""
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
        """Transcribeer audio."""
        if config.OPENAI_WHISPER_ENABLED and config.OPENAI_API_KEY:
            return self._transcribe_openai(audio_path)
        else:
            return self._transcribe_local(audio_path)

    def _transcribe_local(self, audio_path: str) -> str:
        """Lokale Whisper."""
        self._log("Transcriberen (lokaal)...")
        result = self.whisper_model.transcribe(
            audio_path,
            language=config.WHISPER_LANGUAGE,
            initial_prompt=config.WHISPER_PROMPT,
            fp16=False
        )
        text = result["text"].strip()
        return text

    def _transcribe_openai(self, audio_path: str) -> str:
        """OpenAI Whisper API."""
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
            return text
        except Exception as e:
            self._log(f"OpenAI error: {e}, fallback...")
            return self._transcribe_local(audio_path)

    def _type_text(self, text: str):
        """Typ tekst via clipboard."""
        if not text:
            return

        # Filter Whisper hallucinations (stilte = YouTube ondertitels)
        hallucinations = [
            "ondertitels ingediend door de amara.org gemeenschap",
            "ondertitels ingediend door de amara org gemeenschap",
            "thanks for watching",
            "subscribe",
            "bedankt voor het kijken"
        ]

        text_lower = text.lower().strip()
        for hallucination in hallucinations:
            if hallucination in text_lower:
                self._log(f"⚠️  Hallucination gedetecteerd, genegeerd: '{text}'")
                return

        with self.typing_lock:
            self._log(f"✍️  '{text[:50]}...'")
            import subprocess
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            self.keyboard_controller.press(Key.cmd)
            self.keyboard_controller.tap('v')
            self.keyboard_controller.release(Key.cmd)

    def _process_audio(self, audio: np.ndarray):
        """Verwerk audio."""
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
            self._log(f"ERROR: {e}")
        finally:
            self.processing = False

    def run(self):
        """Main loop - wacht op signals."""
        print("=" * 60)
        print("TypTalk Daemon V2 - Signal-based (STABIEL)")
        print("=" * 60)
        print(f"PID: {os.getpid()}")
        print("Wacht op Fn-toets via Karabiner...")
        print("Druk Ctrl+C om te stoppen")
        print("=" * 60)

        # Infinite loop - signals interrumperen dit
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nGestopt.")
        finally:
            if self.pid_file.exists():
                self.pid_file.unlink()


def main():
    """Start daemon."""
    daemon = TypTalkDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
