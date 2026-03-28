from faster_whisper import WhisperModel


class STTService:
    def __init__(self):
        self.model = WhisperModel("base", device="cpu", compute_type="int8")

    def transcribe(self, audio_path) -> str:
        segments, info = self.model.transcribe(audio_path)

        return " ".join([segment.text for segment in segments])
    

# if __name__ == "__main__":
#     stt_service = STTService()
#     result = stt_service.transcribe("test.wav")
#     print(result)

# conf -> piper