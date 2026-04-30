from infra.google.auth import get_credentials
from lib.connectors import URLCaller
from lib.environment import get_conf_for
from skills.base import SkillBase, SkillResult
from email.mime.text import MIMEText
import base64
from lib.log import logger

log = logger.get_logger()


class GmailSend(SkillBase):

    def __init__(self):
        creds = get_credentials()
        self.caller = URLCaller(
            headers={"Authorization": f"Bearer {creds.token}"}
        )
        conf = get_conf_for("gmail")
        self.base_url = conf.get("base_url")
        self.message_endpoint = conf.get("message_endpoint")

    @property
    def name(self) -> str:
        return "gmail.send"
    
    def execute(self, **kwargs) -> SkillResult:
        receiver_email = kwargs.get("to")
        subject = kwargs.get("subject")
        body = kwargs.get("body")

        parse_email_message = self._build_message(to=receiver_email, subject=subject, body=body)

        url =f"{self.base_url}/{self.message_endpoint}/send"
        response = self.caller.perform_single_call(url=url, verb="post", json=parse_email_message)

        if response is None:
            log.error("API returned None")
            return SkillResult(success=False, error="API returned None")

        if response.status != 200:
            log.error(f"API returned status code {response.status}")
            error = f"API returned status code {response.status}"
            return SkillResult(success=False, error=error)

        data = response.json

        return SkillResult(success=True, data={"message_id": data.get("id")})

    def _build_message(self, to: str, subject: str, body: str) -> dict:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        return {"raw": raw}
    

if __name__ == "__main__":
    skill = GmailSend()
    result = skill.execute(
        to="sehajjot20@gmail.com",
        subject="Test from Personal AI OS",
        body="This is a test email sent from the GmailSend skill."
    )
    print(result)