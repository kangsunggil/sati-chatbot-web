
from audio.tts import TTSClient
from core.rag_engine import ask_rag_question, ask_gpt_fallback
from prompts.system_prompt import load_system_prompt

def handle_text_input(messages, rag_chain, tts, meditation_func):
    system_prompt = load_system_prompt()
    print("\n⌨️ 텍스트 입력 모드입니다.")
    print("사티에게 하고싶은 말을 입력해주세요.")
    print("또는 아래 명령어 중 하나를 입력할 수 있어요:")
    print("2 → 음성 대화 모드로 전환")
    print("3 → 명상문 선택 메뉴로 이동")
    print("4 → 프로그램 종료")

    while True:
        print()  # 입력 전 줄바꿈으로 콘솔 깔끔하게
        user_input = input("당신: ").strip()

        if not user_input:
            print("❗ 입력이 비어있습니다. 다시 입력해주세요.")
            continue

        if user_input == "2":
            return "voice"
        elif user_input == "3":
            meditation_func()
        elif user_input == "4":
            print("👋 사티 챗봇을 종료합니다.")
            return "exit"
        else:
            messages.append({"role": "user", "content": user_input})
            full_messages = [{"role": "system", "content": system_prompt}] + messages

            # 먼저 GPT 파인튜닝 응답 시도
            answer = ask_gpt_fallback(full_messages)
            if not answer or "답변할 수 없" in answer or "모르겠" in answer:
                print("🔄 GPT 응답 실패 → RAG 시도")
                answer = ask_rag_question(rag_chain, user_input)

            messages.append({"role": "assistant", "content": answer})
            print(f"사티: {answer}\n")
            tts.speak(answer)
