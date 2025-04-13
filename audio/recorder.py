import pyaudio
import wave
import threading
import os

stop_recording = False

def record_voice_async(filename="input.wav", record_seconds=20):
    def _record():
        global stop_recording
        stop_recording = False

        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 16000

        if os.path.exists(filename):
            os.remove(filename)

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels,
                        rate=rate, input=True, frames_per_buffer=chunk)

        frames = []
        for _ in range(0, int(rate / chunk * record_seconds)):
            if stop_recording:
                break
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))

    thread = threading.Thread(target=_record)
    thread.start()
    return thread
