from faster_whisper import WhisperModel
import webrtcvad
import sounddevice as sd
import numpy as np
import wave
import tempfile



class STTService:
    def __init__(self):
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe(self, audio_path) -> str:
        segments, info = self.model.transcribe(audio_path)

        return " ".join([segment.text for segment in segments])
    

def record_until_silent(sample_rate: int = 16000, frame_duration: int = 30, silence_threshold: float = 1.5) -> str:

    vad = webrtcvad.Vad(2)  # aggressiveness 0-3, 2 is balanced
    frame_size = int(sample_rate * frame_duration / 1000)
    max_silence_frames = int(silence_threshold * 1000 / frame_duration)

    frames = []
    silent_frames  = 0

    with sd.RawInputStream(samplerate=sample_rate, blocksize=frame_size, dtype='int16', channels=1) as stream:
        while True:
            frame, _ = stream.read(frame_size)
            frames.append(frame)
            
            is_speech = vad.is_speech(bytes(frame), sample_rate)
            
            if not is_speech:
                silent_frames  += 1
            else:
                silent_frames = 0  # reset on speech
                
            if silent_frames > max_silence_frames:
                break  # enough silence, stop recording
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        output_path = f.name

        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # int16 = 2 bytes
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join([bytes(f) for f in frames]))

    return output_path      



if __name__ == "__main__":
#     stt_service = STTService()
#     result = stt_service.transcribe("test.wav")
#     print(result)

# conf -> piper

    # path = record_until_silent()
    # print(f"Recorded to: {path}")
    # stt = STTService()
    # print(stt.transcribe(path))