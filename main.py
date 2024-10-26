import speech_recognition as sr
from googletrans import Translator
import pyaudio
import wave
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from gtts import gTTS
import os

class MultiLanguageTranslator:
    def __init__(self):
        """Initialize the translator using googletrans."""
        self.recognizer = sr.Recognizer()
        self.translator = Translator()

        # Languages that can be transliterated into Hinglish
        self.supported_transliteration_langs = {
            'hindi': 'hi',
            'marathi': 'mr',
            'gujarati': 'gu',
            'bengali': 'bn',
            'tamil': 'ta',
            'telugu': 'te',
            'kannada': 'kn',
            'malayalam': 'ml',
            'punjabi': 'pa'
        }

    def record_audio(self, duration=10):
        """Record audio from microphone."""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print(f"Recording for {duration} seconds...")

        frames = []
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Recording finished.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save recording
        audio_file = "temp_recording.wav"
        with wave.open(audio_file, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        return audio_file

    def speech_to_text(self, audio_file):
        """Convert speech to text using Google Speech Recognition."""
        with sr.AudioFile(audio_file) as source:
            audio = self.recognizer.record(source)

        try:
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition; {e}"

    def detect_language(self, text):
        """Detect the language of the given text using googletrans."""
        detected = self.translator.detect(text)
        print(f"Detected language: {detected.lang}")
        return detected.lang

    def translate_text(self, text, target_lang):
        """Translate text to target language using googletrans."""
        translation = self.translator.translate(text, dest=target_lang)
        return translation.text

    def to_hinglish(self, text, lang_code):
        """Convert Indian language text to Hinglish (romanized) form based on detected language."""
        if lang_code == 'hi' or lang_code == 'mr':
            # Convert Devanagari (or similar script) to Roman script (Hinglish)
            hinglish = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        else:
            # For non-Devanagari scripts, further customization needed here
            hinglish = text  # Placeholder, depends on supported script
        return hinglish

    def text_to_speech(self, text, lang='en', filename="output_audio.mp3"):
        """Convert text to speech using gTTS (Google Text-to-Speech)."""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(filename)
            print(f"Audio saved as {filename}")
            os.system(f"start {filename}")  # For Windows, use 'start'. For Linux/Mac, replace with 'open' or 'xdg-open'.
        except Exception as e:
            print(f"Error converting text to speech: {e}")

    def process_speech(self):
        """Process speech to detect language, transliterate if needed, and translate to English, then convert to audio."""
        try:
            # Record audio
            audio_file = self.record_audio()

            # Convert speech to text
            original_text = self.speech_to_text(audio_file)
            print(f"\nOriginal Text: {original_text}")

            # Detect the language of the spoken text
            detected_lang = self.detect_language(original_text)

            # If the detected language is one of the Indian languages that supports transliteration
            if detected_lang in self.supported_transliteration_langs.values():
                hinglish_text = self.to_hinglish(original_text, detected_lang)
                print(f"Hinglish: {hinglish_text}")

            # Translate to English
            translated_text = self.translate_text(original_text, 'en')
            print(f"Translation (English): {translated_text}")

            # Convert translated text to speech and save it as an audio file
            self.text_to_speech(translated_text, lang='en')

        except Exception as e:
            print(f"Error occurred: {e}")

def main():
    # Initialize translator
    translator = MultiLanguageTranslator()

    while True:
        # Process speech (automatically detects language, translates to English, and converts to Hinglish if applicable)
        translator.process_speech()

        # Ask to continue
        if input("\nContinue? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main()
