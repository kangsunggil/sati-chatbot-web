from openai import OpenAI
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio(filepath="input.wav"):
    with open(filepath, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ko",
            prompt="이 대화는 마음챙김, 감정, 명상과 관련된 내용입니다."
        )
    return transcript.text
