from infra.google.auth import get_credentials
from lib.connectors import URLCaller
from lib.environment import get_conf_for
from lib.log import logger
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from skills.base import SkillBase, SkillResult

log = logger.get_logger()


class CalendarRead(SkillBase):
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
        return "calendar.read"
    
    def execute(self, **kwargs):

        days_ahead = kwargs.get("days_ahead", 7)
        events_raw_data = self._get_all_events_raw_data(days_ahead)
        events = []

        for raw_event in events_raw_data:
            event = self._parse_events_from_raw_data(raw_event)
            events.append(event)
        
        return SkillResult(success=True, data={"events": events})

    def _get_all_events_raw_data(self, days_ahead: int = 7) -> list | None:

        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days_ahead)).isoformat()
        
        params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "maxResults": 20,
            "singleEvents": "true",
            "orderBy": "startTime"
        }
        url = f"{self.base_url}/{self.events_endpoint}"
        response = self.caller.perform_single_call(url=url, params=params)

        if response is None:
            log.error("API return None")
            return None
        
        if response.status != 200:
            log.error(f"API returned status code {response.status}")
            return None
        
        data = response.json

        events = data.get("items")
        return events
    
    def _parse_events_from_raw_data(self, raw_data: dict):

        summary = raw_data.get("summary", "")

        start_data = raw_data.get("start")
        start_time = start_data.get("dateTime") or start_data.get("date")
        start_dt = datetime.fromisoformat(start_time)
        start_dt_berlin = start_dt.astimezone(ZoneInfo("Europe/Berlin"))

        end_data = raw_data.get("end")
        end_time = end_data.get("dateTime") or end_data.get("date")
        end_dt = datetime.fromisoformat(end_time)
        end_dt_berlin = end_dt.astimezone(ZoneInfo("Europe/Berlin"))

        description = raw_data.get("description")
        location = raw_data.get("location")

        return {
            "summary": summary,
            "start": start_dt_berlin,
            "end": end_dt_berlin,
            "description": description,
            "location": location
        }


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    skill = CalendarRead()
    result = skill.execute()
    print(result)
