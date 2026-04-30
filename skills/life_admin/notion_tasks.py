# from lib.cache import JSONFileCache
# from lib.connectors import URLCaller
# from lib.environment import get_conf_for

# api_key = get_conf_for("notion").get("api_key")
# version = get_conf_for("notion").get("version")
# database_id = get_conf_for("notion").get("todo_database_id")

# # url = "https://api.notion.com/v1/search"
# url = f"https://api.notion.com/v1/databases/{database_id}/query"

# # POST https://api.notion.com/v1/databases/{database_id}/query


# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Notion-Version": version,
#     "Content-Type": "application/json"
# }

# json = {"filter": {"value": "database", "property": "object"}}
# caller = URLCaller(headers=headers)
# response = caller.perform_single_call(url=url, verb="post")
# JSONFileCache(name="notion_databases").save(data=response.json)
# # print(response.json)




from lib.connectors import URLCaller
from lib.environment import get_conf_for
from lib.log import logger
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from skills.base import SkillBase, SkillResult

log = logger.get_logger()


class NotionReadTasks(SkillBase):
    def __init__(self):
        conf = get_conf_for("notion")
        self.api_key = conf.get("api_key")
        self.version = conf.get("version")
        self.database_id = conf.get("todo_database_id")
        self.base_url = conf.get("base_url")
        self.database_endpoint = conf.get("database_endpoint")

        self.caller = URLCaller(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.version,
                "Content-Type": "application/json"
            }
        )
    
    @property
    def name(self) -> str:
        return "notion.read_tasks"
    
    def execute(self, **kwargs) -> SkillResult:
        raw_data = self._get_all_tasks_raw_data()

        tasks = self._parse_tasks_from_raw_data(raw_data)

        if not tasks:
            log.info("No tasks found in Notion database.")
            return SkillResult(success=True, data={"tasks": []})

        return SkillResult(success=True, data={"tasks": tasks})
    
    def _get_all_tasks_raw_data(self) -> list | None:
        url = f"{self.base_url}/{self.database_endpoint}/{self.database_id}/query"
        response = self.caller.perform_single_call(url=url, verb="post")

        if response is None:
            log.error("API returned None")
            return SkillResult(success=False, error="API returned None")

        if response.status != 200:
            log.error(f"API returned status code {response.status}")
            error = f"API returned status code {response.status}"
            return SkillResult(success=False, error=error)

        data = response.json
        return data.get("results")
    
    def _parse_tasks_from_raw_data(self, raw_data: dict) -> list:
        if not raw_data:
            return []
        tasks = []
        for item in raw_data:
            properties = item.get("properties", {})
            status_raw_data = properties.get("Status", {})
            status = status_raw_data.get("status", {}).get("name", "unknown")

            title_prop = properties.get("Task name", {})
            title_arr = title_prop.get("title", [])
            task_name = title_arr[0].get("plain_text", "") if title_arr else ""

            due_date_prop = properties.get("Due date", {})
            due_date_raw = due_date_prop.get("date", {})
            due_date = due_date_raw.get("start") if due_date_raw else None

            url = item.get("url", "")

            task = {
                "task_name": task_name,
                "status": status,
                "due_date": due_date,
                "url": url
            }
            tasks.append(task)
        
        return tasks
    

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    skill = NotionReadTasks()
    result = skill.execute()
    print(result)