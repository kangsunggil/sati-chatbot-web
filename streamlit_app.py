# streamlit_app.py

import streamlit as st
import os
from prompts.system_prompt import load_system_prompt
from core.rag_engine import init_rag, ask_rag_question, ask_gpt_fallback
from core.meditation import read_meditation_text
from audio.tts import TTSClient
from audio.transcriber import transcribe_audio
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from realtime_audio import AudioFrameRecorder

st.set_page_config(page_title="사티 챗봇", layout="centered")
st.title("🧘 사티 마음챙김 챗봇")
st.markdown("사티는 당신의 내면을 위한 조용한 친구입니다.")

# 초기화
rag_chain = init_rag("Mindfulness RAG")
system_prompt = load_system_prompt()
tts = TTSClient()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

mode = st.radio("모드를 선택하세요:", ["텍스트 채팅", "음성 채팅", "명상문"])

# --- 텍스트 채팅 모드 ---
if mode == "텍스트 채팅":
    st.subheader("💬 사티와 채팅하세요")
    user_input = st.chat_input("사티에게 물어보세요")

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("사티가 생각 중입니다..."):
                full_messages = st.session_state.messages
                answer = ask_gpt_fallback(full_messages)
                if not answer or "모르겠" in answer:
                    st.info("GPT 답변이 부족해요. 문서를 검색합니다.")
                    answer = ask_rag_question(rag_chain, user_input)

                st.markdown(answer)
                tts.speak(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

# --- 음성 채팅 모드 ---
elif mode == "음성 채팅":
    st.subheader("🎤 음성 입력 방식 선택")
    input_mode = st.radio("입력 방법:", ["파일 업로드", "실시간 마이크 녹음"])

    if input_mode == "파일 업로드":
        uploaded_file = st.file_uploader("음성 파일 업로드 (WAV 또는 MP3)", type=["wav", "mp3"])
        if uploaded_file:
            with open("temp_audio.wav", "wb") as f:
                f.write(uploaded_file.read())
            try:
                user_input = transcribe_audio("temp_audio.wav")
                st.success(f"🗣️ 인식된 질문: {user_input}")
                st.session_state.messages.append({"role": "user", "content": user_input})

                with st.chat_message("assistant"):
                    with st.spinner("사티가 응답 중입니다..."):
                        full_messages = st.session_state.messages
                        answer = ask_gpt_fallback(full_messages)
                        if not answer or "모르겠" in answer:
                            st.info("RAG 문서 검색 중...")
                            answer = ask_rag_question(rag_chain, user_input)
                        st.markdown(answer)
                        tts.speak(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                st.error(f"음성 인식 실패: {e}")

    elif input_mode == "실시간 마이크 녹음":
        st.info("🎙️ 마이크에 대고 말씀해주세요. 중지 버튼 누르면 처리됩니다.")
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
                            full_messages = st.session_state.messages
                            answer = ask_gpt_fallback(full_messages)
                            if not answer or "모르겠" in answer:
                                st.info("RAG 문서 검색 중...")
                                answer = ask_rag_question(rag_chain, user_input)
                            st.markdown(answer)
                            tts.speak(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"❌ Whisper 오류: {e}")

# --- 명상문 보기/재생 모드 ---
elif mode == "명상문":
    st.subheader("🧘 명상문 선택 및 듣기")
    folder_path = "mindfulness meditation"
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    if not files:
        st.warning("명상문이 없습니다.")
    else:
        options = ["무작위 명상문"] + files
        selected = st.selectbox("명상문 선택:", options)

        if st.button("명상문 보기 및 재생"):
            filepath = os.path.join(folder_path, files[0] if selected == "무작위 명상문" else selected)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    st.text_area("📖 명상문 내용", content, height=300)
                    tts.speak(content, is_meditation=True)
            except Exception as e:
                st.error(f"명상문 로딩 실패: {e}")

