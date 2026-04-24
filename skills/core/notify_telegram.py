from lib.connectors import URLCaller
from lib.environment import get_conf_for
from skills.base import SkillBase, SkillResult


class NotifyTelegramMsg(SkillBase):

    def __init__(self):
        conf = get_conf_for("telegram")
        self.token = conf["bot_token"]
        self.chat_id = conf["chat_id"]
        self.base_url = conf["base_url"]
        self.caller = URLCaller()

    @property
    def name(self) -> str:
        return "notify.telegram_msg"

    def execute(self, **kwargs) -> SkillResult:

        url = f"{self.base_url}{self.token}/sendMessage"

        data = {
            "chat_id": self.chat_id,
            "text": kwargs.get("message", "")
        }
        try:
            response = self.caller.perform_single_call(url=url, verb="post", json=data)
        except Exception as e:
            return SkillResult(success=False, error=str(e))
        
        if response.status != 200:
            return SkillResult(success=False, error=f"Telegram API returned status code {response.status}")
        
        return SkillResult(success=True, data=response.json)


if __name__ == "__main__":
    skill = NotifyTelegramMsg()
    result = skill.execute(message="Hello from Personal AI OS!")
    print(result)