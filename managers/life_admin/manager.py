

import json

from managers.base import BaseManager, ManagerRequest, ManagerResponse
from shared.ollama_service import OllamaService
from skills.life_admin.calendar_read import CalendarRead
from skills.life_admin.calendar_write import CalendarWrite
from skills.life_admin.gmail_read import GmailRead
from skills.life_admin.gmail_send import GmailSend
from skills.life_admin.notion_tasks import NotionReadTasks
from skills.life_admin.notion_write import NotionAddTask

from lib.log import logger 
log = logger.get_logger()

class LifeAdminManager(BaseManager):
    def __init__(self, ollama: OllamaService):
        self.ollama = ollama
        self.skills = {
            "gmail.read": GmailRead(),
            "gmail.send": GmailSend(),
            "calendar.read": CalendarRead(),
            "calendar.write": CalendarWrite(),
            "notion.read_tasks": NotionReadTasks(),
            "notion.add_task": NotionAddTask(),
        }

    @property
    def name(self) -> str:
        return "life_admin"

    def process(self, request: ManagerRequest) -> ManagerResponse:
        task = request.task

        if task == "ping":
            return ManagerResponse(
                manager=self.name,
                status="success",
                summary="pong"
            )

        prompt = f"""You are a skill router. Your ONLY job is to output a single JSON object.

            Task: {task}

            Available skills:
            - gmail.read: read emails from inbox
            - gmail.send: send an email (needs: to, subject, body)
            - calendar.read: read upcoming calendar events
            - calendar.write: create a calendar event (needs: summary, start_time, end_time)
            - notion.read_tasks: read tasks from Notion
            - notion.add_task: add a task to Notion (needs: task dict with name, due_date)

            Output EXACTLY this format and nothing else:
            {{"skill": "gmail.read", "params": {{}}}}

            Task to route: {task}"""
        raw = self.ollama.generate(prompt, model="mistral:7b")
        raw = raw.strip().strip("```json").strip("```").strip()

        try:
            decision = json.loads(raw)
        except json.JSONDecodeError:
            return ManagerResponse(
                manager=self.name,
                status="failed",
                summary="Failed to parse skill decision from LLM"
            )
        
        skill_name = decision.get("skill")
        params = decision.get("params", {})

        if not skill_name:
            return ManagerResponse(
                manager=self.name,
                status="failed",
                summary=f"Unknown skill: {skill_name}"
            )
        
        skill = self.skills.get(skill_name)

        if not skill:
            return ManagerResponse(
                manager=self.name,
                status="failed",
                summary=f"Skill not implemented: {skill_name}"
            )

        result = skill.execute(**params)

        return ManagerResponse(
            manager=self.name,
            status="success" if result.success else "failed",
            summary=str(result.data),
            data=result.data or {},
            alerts=[]
)