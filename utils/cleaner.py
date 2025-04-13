import re

def clean_text(text: str) -> str:
    # 대표 이모티콘 제거
    text = re.sub(r"[:;=8][-^']?[)D\(pP]", "", text)  # :) ;-) :D :(
    # 일반 특수문자 제거
    text = re.sub(r"[☆★♥♡※→←▶◀▽△↑↓▶▶▷◁♬♪♩♭]", "", text)
    # 한글, 영문, 숫자, 문장부호 외 제거
    text = re.sub(r"[^\w가-힣 .,?!]", "", text)
    # 연속 마침표 정리
    text = re.sub(r"[.]{2,}", ".", text)
    # 중복 공백 제거
    text = re.sub(r"\s+", " ", text)
    return text.strip()
