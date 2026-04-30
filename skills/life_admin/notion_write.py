
from lib.connectors import URLCaller
from lib.environment import get_conf_for
from lib.log import logger
from skills.base import SkillBase, SkillResult

log = logger.get_logger()


class NotionAddTask(SkillBase):
    def __init__(self):
        conf = get_conf_for("notion")
        self.api_key = conf.get("api_key")
        self.version = conf.get("version")
        self.database_id = conf.get("todo_database_id")
        self.base_url = conf.get("base_url")
        self.page_endpoint = conf.get("page_endpoint")

        self.caller = URLCaller(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": self.version,
                "Content-Type": "application/json"
            }
        )
    
    @property
    def name(self) -> str:
        return "notion.add_task"
    
    def execute(self, **kwargs) -> SkillResult:
        task = kwargs.get("task")
        if not task:
            log.error("No task provided")
            return SkillResult(success=False, error="No task provided")
        
        payload = self._build_page_body(task)
        url = f"{self.base_url}/{self.page_endpoint}"
        response = self.caller.perform_single_call(url=url, verb="post", json=payload)
        
        if response is None:
            log.error("API returned None")
            return SkillResult(success=False, error="API returned None")
        
        if response.status != 200:
            log.error(f"API returned status code {response.status}")
            error = f"API returned status code {response.status}"
            return SkillResult(success=False, error=error)
        
        data = response.json
        
        return SkillResult(success=True, data={"page_id": data.get("id"), "url": data.get("url")})

    def _build_page_body(self, task: dict) -> dict:
        properties = {
            "Task name": {
                "title": [{"text": {"content": task.get("name", "")}}]
            },
            "Status": {
                "status": {"name": task.get("status", "Not started")}
            }
        }
        
        if task.get("due_date"):
            properties["Due date"] = {
                "date": {"start": task.get("due_date")}
            }
        
        return {
            "parent": {"database_id": self.database_id},
            "properties": properties
        }
    

if __name__ == "__main__":
    skill = NotionAddTask()
    result = skill.execute(task={"name": "Test Task", "status": "In Progress", "due_date": "2024-12-31"})
    print(result)