from core.rag_engine import init_rag, ask_rag_question, ask_gpt_fallback
from core.chat_voice import speak_and_listen
from core.chat_text import handle_text_input
from core.meditation import show_meditation_menu, read_meditation_text
from audio.tts import TTSClient
from prompts.system_prompt import load_system_prompt
import os

def run_chat():
    meditation_path = "C:/Users/pc/Desktop/file_organizer_agent/sati_chatbot_modular/mindfulness meditation"
    rag_chain = init_rag(folder_path="C:/Users/pc/Desktop/file_organizer_agent/sati_chatbot_modular/Mindfulness RAG")
    system_prompt = load_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]
    tts = TTSClient()

    print("\n사티 챗봇을 시작합니다. 아래 메뉴 중 하나를 선택하세요.")

    while True:
        print("\n1. 음성 대화 🎤")
        print("2. 텍스트 입력 ⌨️")
        print("3. 명상문 선택 📄")
        print("4. 종료 ❌")
        mode = input("번호를 입력하세요: ").strip()

        if mode == "1":
            answer = "무엇이 궁금하신가요?"
            while True:
                result = speak_and_listen(answer, messages, meditation_path, rag_chain)
                if result == "text":
                    break
                elif result == "meditation":
                    while True:
                        selected = show_meditation_menu(meditation_path)
                        if selected == "back":
                            break
                        elif selected == "exit":
                            return
                        elif selected:
                            read_meditation_text(selected)
                else:
                    answer = ""  # 🔥 항상 초기화

        elif mode == "2":
            result = handle_text_input(messages, rag_chain, tts, lambda: show_and_read(meditation_path))
            if result == "exit":
                break
            elif result == "voice":
                continue

        elif mode == "3":
            while True:
                result = show_meditation_menu(meditation_path)
                if result == "back":
                    break
                elif result == "exit":
                    return
                elif result:
                    read_meditation_text(result)

        elif mode == "4":
            print("👋 사티 챗봇을 종료합니다.")
            break
        else:
            print("❌ 올바른 번호를 입력해주세요.")

def show_and_read(meditation_path):
    while True:
        result = show_meditation_menu(meditation_path)
        if result == "back":
            break
        elif result == "exit":
            exit(0)
        elif result:
            read_meditation_text(result)
