
from audio.recorder import record_voice_async, stop_recording
from audio.transcriber import transcribe_audio
from audio.tts import TTSClient
from core.rag_engine import ask_rag_question, ask_gpt_fallback
from prompts.system_prompt import load_system_prompt
import time
import threading

def speak_and_listen(previous_answer, messages, meditation_path, rag_chain=None):
    tts = TTSClient()
    system_prompt = load_system_prompt()

    if previous_answer:
        print(f"사티: {previous_answer}")
        tts.speak(previous_answer)

    print("\n[이제 사티에게 무엇이든 이야기해주세요.\n단, 시끄러운 환경의 경우나 아무것도 이야기하지 않는 경우 음성인식의 오류가 발생할 수 있습니다.]")
    print("\n[선택지] 1. 내 답변 완료 | 2. 일시 정지 | 3. 텍스트 입력으로 전환 | 4. 명상문 선택 | 5. 종료")

    global stop_recording
    stop_recording = False
    recorder_thread = record_voice_async(record_seconds=15)

    user_choice = None
    def wait_for_user_input():
        nonlocal user_choice
        while user_choice is None:
            try:
                choice = input("> ").strip()
                if choice in ["1", "2", "3", "4", "5"]:
                    user_choice = choice
                    break
            except EOFError:
                break

    input_thread = threading.Thread(target=wait_for_user_input)
    input_thread.daemon = True
    input_thread.start()

    start_time = time.time()
    while time.time() - start_time < 15 and user_choice is None:
        time.sleep(0.1)

    if user_choice is None:
        user_choice = "1"
        print("⏱️ 15초가 지나 자동으로 응답을 처리합니다.")

    if recorder_thread.is_alive():
        stop_recording = True
        recorder_thread.join()

    if user_choice == "2":
        print("⏸️ 일시 정지되었습니다. 다시 시작하려면 2를 입력하세요.")
        while True:
            resume = input("재시작하시려면 2를 입력하세요: ").strip()
            if resume == "2":
                return "voice"
    elif user_choice == "3":
        return "text"
    elif user_choice == "4":
        return "meditation"
    elif user_choice == "5":
        print("👋 사티 챗봇을 종료합니다.")
        exit(0)

    try:
        user_input = transcribe_audio()
        print(f"당신(음성): {user_input}")
    except Exception as e:
        print("❌ 음성 인식 실패:", e)
        return "voice"

    messages.append({"role": "user", "content": user_input})
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    answer = ask_gpt_fallback(full_messages)
    if not answer or "답변할 수 없" in answer or "모르겠" in answer:
        print("🔄 GPT 응답 실패 → RAG 시도")
        answer = ask_rag_question(rag_chain, user_input)

    messages.append({"role": "assistant", "content": answer})
    print(f"사티: {answer}")
    tts.speak(answer)
    return ""
