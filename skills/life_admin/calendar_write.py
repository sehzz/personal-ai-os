from infra.google.auth import get_credentials
from lib.connectors import URLCaller
from lib.environment import get_conf_for
from lib.log import logger
from datetime import datetime, timedelta, timezone
from skills.base import SkillBase, SkillResult

log = logger.get_logger()


class CalendarWrite(SkillBase):
    def __init__(self):
        creds = get_credentials()
        self.caller = URLCaller(
            headers={"Authorization": f"Bearer {creds.token}"}
        )
        conf = get_conf_for("google_calender")
        self.base_url = conf.get("base_url")
        self.events_endpoint = conf.get("events_endpoint")

    @property
    def name(self) -> str:
        return "calendar.write"
    
    def execute(self, **kwargs):
        summary = kwargs.get("summary")
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        description = kwargs.get("description", "")

        event_body = self._build_event_body(
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description
        )
        url = f"{self.base_url}/{self.events_endpoint}"
        response = self.caller.perform_single_call(verb="POST", url=url, json=event_body)

        if response is None:
            log.error("API returned None")
            return SkillResult(success=False, error="API returned None")

        if response.status != 200:
            log.error(f"API returned status code {response.status}")
            error = f"API returned status code {response.status}"
            return SkillResult(success=False, error=error)

        data = response.json

        return SkillResult(success=True, data={"message_id": data.get("id")})

    
    def _build_event_body(
            self,
            summary: str,
            start_time: datetime,
            end_time: datetime,
            description: str = ""
            ) -> dict:

        event_body = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Europe/Berlin"
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "Europe/Berlin"
            }
        }     

        return event_body
    

if __name__ == "__main__":
    skill = CalendarWrite()
    rskill = CalendarWrite()
    result = skill.execute(
        summary="Test event from Personal AI OS",
        start_time=datetime.now(timezone.utc) + timedelta(days=1),
        end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
        description="This is a test event"
    )
    print(result)