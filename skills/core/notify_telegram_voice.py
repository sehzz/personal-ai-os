import os

from lib.connectors import URLCaller
from lib.environment import get_conf_for
from skills.base import SkillBase, SkillResult
from voice.tts import TTSService


class NotifyTelegramVoice(SkillBase):

    def __init__(self, tts_service: TTSService):
        conf = get_conf_for("telegram")
        self.tts = tts_service
        self.token = conf["bot_token"]
        self.chat_id = conf["chat_id"]
        self.base_url = conf["base_url"]
        self.caller = URLCaller()

    @property
    def name(self) -> str:
        return "notify.telegram_voice"

    def execute(self, **kwargs) -> SkillResult:
        message = kwargs.get("message", "")
        output_path = self.tts.generate(text=message)
        url = f"{self.base_url}{self.token}/sendVoice"

        try:
            with open(output_path, "rb") as audio_file:
                response = self.caller.perform_single_call(
                    url=url,
                    verb="post",
                    data={"chat_id": self.chat_id},
                    files={"voice": audio_file}
                )
        except Exception as e:
            return SkillResult(success=False, error=str(e))
        
        if response.status != 200:
            return SkillResult(success=False, error=f"Telegram API returned status code {response.status}")
        
        os.remove(output_path)
        
        return SkillResult(success=True, data=response.json)


if __name__ == "__main__":
    tts = TTSService()
    skill = NotifyTelegramVoice(tts_service=tts)
    result = skill.execute(message="Hello this is a voice test from Personal AI OS")
    print(result)