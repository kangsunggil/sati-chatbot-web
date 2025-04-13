import os
import tempfile
from google.cloud import texttospeech
from utils.cleaner import clean_text
import subprocess
import threading

class TTSClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = texttospeech.TextToSpeechClient()
        return cls._instance

    def speak(self, text, lang="ko-KR", is_meditation=False):
        cleaned_text = clean_text(text)
        synthesis_input = texttospeech.SynthesisInput(text=cleaned_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang,
            name="ko-KR-Wavenet-B",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.85
        )
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        temp_path = os.path.join(os.getcwd(), "temp_speech.wav")
        with open(temp_path, "wb") as out:
            out.write(response.audio_content)

        def play():
            if is_meditation:
                print("🎧 [명상문 재생 중입니다...]")
            else:
                print("🔊 [사티 응답 재생 중입니다...]")
            subprocess.run([
                "powershell",
                "-c",
                f'$player = New-Object System.Media.SoundPlayer "{temp_path}"; $player.PlaySync();'
            ])

        thread = threading.Thread(target=play)
        thread.start()
        thread.join()

        if os.path.exists(temp_path):
            os.remove(temp_path)
