# realtime_audio.py

import av
import numpy as np
import soundfile as sf
import uuid
import os

class AudioFrameRecorder:
    def __init__(self, output_dir="recordings"):
        self.frames = []
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def __call__(self, frame: av.AudioFrame):
        audio = frame.to_ndarray().flatten().astype(np.int16)
        self.frames.append(audio)

    def save_wav(self):
        if not self.frames:
            return None
        output_path = os.path.join(self.output_dir, f"{uuid.uuid4()}.wav")
        audio_data = np.concatenate(self.frames)
        sf.write(output_path, audio_data, 48000, 'PCM_16')
        return output_path
