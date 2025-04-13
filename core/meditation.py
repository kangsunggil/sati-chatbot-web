import os
from audio.tts import TTSClient

def show_meditation_menu(folder_path):
    print("\n🧘 마음챙김 명상문을 선택해보세요:")
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    if not files:
        print("❌ 명상문이 없습니다.")
        return None

    print("0. 오늘 하루를 위한 무작위 마음챙김 명상문 🌿")
    for idx, name in enumerate(files):
        print(f"{idx+1}. {name}")
    print("99. 메인 메뉴로 돌아가기")
    print("100. 프로그램 종료")

    try:
        choice = int(input("번호를 입력하세요: ").strip())
        if choice == 99:
            return "back"
        elif choice == 100:
            return "exit"
        elif choice == 0:
            return os.path.join(folder_path, files[0])
        elif 1 <= choice <= len(files):
            return os.path.join(folder_path, files[choice - 1])
        else:
            print("❌ 잘못된 입력입니다.")
            return None
    except:
        print("❌ 숫자를 정확히 입력해주세요.")
        return None

def read_meditation_text(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            print("\n📖 명상문:")
            print(content)
            TTSClient().speak(content, is_meditation=True)
    except Exception as e:
        print("❌ 명상문을 불러올 수 없습니다:", e)
