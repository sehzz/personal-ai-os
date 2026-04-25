from infra.google.auth import get_credentials
from lib.connectors import URLCaller
from lib.environment import get_conf_for
from lib.log import logger
from skills.base import SkillBase, SkillResult

log = logger.get_logger()


class GmailRead(SkillBase):
    
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
        return "gmail.read"
    
    def execute(self, **kwargs) -> SkillResult:
        message_ids = self._get_message_ids(self.caller)
        if isinstance(message_ids, str):
            return SkillResult(success=False, error=message_ids)

        email_list = []

        for message_id in message_ids:
            id = message_id.get("id")
            raw_email_data = self._get_raw_email_data_from_id(id, self.caller)
            if isinstance(raw_email_data, str):
                continue

            parse_data = self._parse_email_from_raw_data(raw_email_data)
            email_list.append(parse_data)

        return SkillResult(success=True, data={"emails": email_list})

    def _get_message_ids(self, caller: URLCaller) -> list | str:
    
        params = {"maxResults": 10}
        url = f"{self.base_url}/{self.message_endpoint}"
        response = caller.perform_single_call(url=url, params=params)

        if response is None:
            log.error("API returned None")

        if response.status != 200:
            log.error(f"API returned status code {response.status}")
            return f"API returned status code {response.status}"
        
        data = response.json
        message_ids = data.get("messages")

        return message_ids

    def _get_raw_email_data_from_id(self, message_id: str, caller: URLCaller) -> dict | str:
            
        url = f"{self.base_url}/{self.message_endpoint}/{message_id}"
        response = caller.perform_single_call(url=url)

        if response is None:
            log.error("API returned None")

        if response.status != 200:
            log.error(f"API returned status code {response.status}")
            return f"API returned status code {response.status}"

        return response.json

    def _parse_email_from_raw_data(self, raw_data: dict) -> dict:
        snippet = raw_data.get("snippet", "")
        payload = raw_data.get("payload")
        headers = payload.get("headers") or []
        header_map = {h.get("name"): h.get("value") for h in headers}

        return {
            "subject": header_map.get("Subject", ""),
            "from": header_map.get("From", ""),
            "snippet": snippet,
            "date": header_map.get("Date", "")
        }

        
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    skill = GmailRead()
    result = skill.execute()
    print(result)