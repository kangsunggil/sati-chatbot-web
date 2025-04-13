def load_system_prompt(filepath="prompts/secure_system_prompt.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "사티는 마음챙김을 돕는 따뜻한 대화 상대입니다."
