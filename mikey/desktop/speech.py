"""Optional voice features: microphone speech recognition and reading replies aloud."""

from __future__ import annotations

import re
import sys
import threading

# PyAudioWPatch publishes Windows wheels for newer Python versions. Make its
# compatible PyAudio API visible to SpeechRecognition without compiling PyAudio.
try:
    import pyaudiowpatch as _pyaudio
    sys.modules.setdefault("pyaudio", _pyaudio)
except ImportError:
    _pyaudio = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


def voice_input_available() -> bool:
    return bool(sr and _pyaudio)


class Speaker:
    """Reads text aloud with pyttsx3 on a background thread, when it is installed."""

    def __init__(self) -> None:
        self._engine = None
        self._lock = threading.Lock()
        if pyttsx3:
            try:
                self._engine = pyttsx3.init()
            except Exception:
                pass

    def say(self, text: str, bangla: bool = False) -> None:
        if not self._engine:
            return

        def worker():
            try:
                with self._lock:
                    # Use an installed Bengali SAPI voice when one exists; otherwise
                    # use the system's default voice without blocking the UI.
                    if bangla:
                        voices = self._engine.getProperty("voices")
                        match = next((v for v in voices if re.search(r"bangla|bengali|বাংলা", (v.name + " " + v.id), re.I)), None)
                        if match:
                            self._engine.setProperty("voice", match.id)
                    self._engine.say(text)
                    self._engine.runAndWait()
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def stop(self) -> None:
        try:
            if self._engine:
                self._engine.stop()
        except Exception:
            pass
