import os
import streamlit as st
from dotenv import load_dotenv

# 환경변수 로드 및 설정
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# 모듈 import (구조 기반)
from core.rag_engine import init_rag, ask_rag_question, ask_gpt_fallback
from meditation.loader import show_meditation_menu
from meditation.reader import read_meditation_text
from audio.tts import TTSClient
from audio.transcriber import transcribe_audio
from realtime_audio import AudioFrameRecorder
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# TTS 클라이언트 초기화
tts = TTSClient()

# 페이지 설정
st.set_page_config(page_title="사티 챗봇", layout="centered")
st.title("🧘 사티 마음챙김 챗봇")
st.markdown("사티는 당신의 내면을 위한 조용한 친구입니다.")

# 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 메뉴 선택
mode = st.radio("모드를 선택하세요:", ["텍스트 채팅", "음성 채팅", "명상문"])

def handle_text_chat():
    st.subheader("💬 사티와 채팅하세요")
    user_input = st.chat_input("사티에게 물어보세요")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("사티가 생각 중입니다..."):
                rag_chain = init_rag("Mindfulness RAG")
                answer = ask_gpt_fallback(st.session_state.messages)
                if not answer or "모르겠" in answer:
                    st.info("문서를 검색해 더 나은 답변을 찾습니다.")
                    answer = ask_rag_question(rag_chain, user_input)

                st.markdown(answer)
                tts.speak(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

def handle_voice_chat():
    st.subheader("🎤 음성으로 질문하고 사티의 음성을 들어보세요")

    input_mode = st.radio("입력 방식 선택", ["파일 업로드", "실시간 마이크"])

    if input_mode == "파일 업로드":
        uploaded_file = st.file_uploader("WAV 또는 MP3 파일 업로드", type=["wav", "mp3"])
        if uploaded_file:
            with open("temp_audio.wav", "wb") as f:
                f.write(uploaded_file.read())
            try:
                user_input = transcribe_audio("temp_audio.wav")
                st.success(f"🗣️ 인식된 질문: {user_input}")
                st.session_state.messages.append({"role": "user", "content": user_input})

                with st.chat_message("assistant"):
                    with st.spinner("사티가 응답 중입니다..."):
                        rag_chain = init_rag("Mindfulness RAG")
                        answer = ask_gpt_fallback(st.session_state.messages)
                        if not answer or "모르겠" in answer:
                            st.info("문서를 검색해 더 나은 답변을 찾습니다.")
                            answer = ask_rag_question(rag_chain, user_input)

                        st.markdown(answer)
                        tts.speak(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"음성 인식 중 오류 발생: {e}")

    elif input_mode == "실시간 마이크":
        st.info("마이크에 대고 말씀해주세요. 중지 후 분석됩니다.")
        recorder = AudioFrameRecorder()
        webrtc_ctx = webrtc_streamer(
            key="speech",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=1024,
            audio_frame_callback=recorder,
        )

        if st.button("⏹️ 녹음 중지 및 처리"):
            filepath = recorder.save_wav()
            if filepath:
                st.audio(filepath, format="audio/wav")
                try:
                    user_input = transcribe_audio(filepath)
                    st.success(f"🗣️ 인식된 질문: {user_input}")
                    st.session_state.messages.append({"role": "user", "content": user_input})

                    with st.chat_message("assistant"):
                        with st.spinner("사티가 응답 중입니다..."):
                            rag_chain = init_rag("Mindfulness RAG")
                            answer = ask_gpt_fallback(st.session_state.messages)
                            if not answer or "모르겠" in answer:
                                st.info("문서를 검색해 더 나은 답변을 찾습니다.")
                                answer = ask_rag_question(rag_chain, user_input)

                            st.markdown(answer)
                            tts.speak(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"❌ Whisper 오류: {e}")

def handle_meditation():
    st.subheader("🧘 명상문 보기 및 듣기")
    try:
        filepath = show_meditation_menu("mindfulness meditation")
        if filepath:
            content = read_meditation_text(filepath)
            st.text_area("명상문 내용", content, height=300)
            tts.speak(content, is_meditation=True)
    except Exception as e:
        st.error(f"명상문 처리 중 오류 발생: {e}")

# 메인 실행 분기
if mode == "텍스트 채팅":
    handle_text_chat()
elif mode == "음성 채팅":
    handle_voice_chat()
elif mode == "명상문":
    handle_meditation()
