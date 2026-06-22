"""
voice_service.py
-----------------
Handles voice-related features:
 - Speech-to-Text (microphone input) using SpeechRecognition
 - Text-to-Speech (reading translations aloud) using pyttsx3

Both run in background threads from the GUI layer to avoid freezing the UI.
"""

import pyttsx3
import speech_recognition as sr


class VoiceError(Exception):
    """Custom exception raised when voice input/output fails."""
    pass


class VoiceService:
    """Provides speech recognition (mic -> text) and text-to-speech (text -> audio)."""

    def __init__(self):
        self._recognizer = sr.Recognizer()
        # pyttsx3 engine is created fresh per call (safer across threads)

    def listen_from_microphone(self, language_code: str = "en") -> str:
        """
        Capture audio from the default microphone and convert it to text.
        Blocking call -- should be run on a background thread by the caller.
        """
        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self._recognizer.listen(source, timeout=6, phrase_time_limit=15)
        except OSError as exc:
            raise VoiceError("No microphone was found on this device.") from exc
        except sr.WaitTimeoutError as exc:
            raise VoiceError("No speech detected. Please try again.") from exc

        try:
            # Google Web Speech API used by SpeechRecognition for recognition
            text = self._recognizer.recognize_google(audio, language=language_code)
            return text
        except sr.UnknownValueError as exc:
            raise VoiceError("Could not understand the audio. Please speak clearly.") from exc
        except sr.RequestError as exc:
            raise VoiceError("Speech recognition service unavailable. Check your internet.") from exc

    def speak_text(self, text: str, rate: int = 170) -> None:
        """
        Convert text to speech and play it aloud.
        Blocking call -- should be run on a background thread by the caller.
        """
        if not text or not text.strip():
            raise VoiceError("There is no text to speak.")
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", rate)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as exc:
            raise VoiceError("Text-to-speech failed on this device.") from exc
