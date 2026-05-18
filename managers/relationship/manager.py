import json

from managers.base import BaseManager, ManagerRequest, ManagerResponse
from shared.ollama_service import OllamaService
from skills.relationships.contacts_read import ContactsRead


class RelationshipManager(BaseManager):
    def __init__(self, ollama: OllamaService):
        self.ollama = ollama
        self.skills = {
            "contacts.read": ContactsRead(),
        }

    @property
    def name(self) -> str:
        return "relationships"

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
            - contacts.read: read relationship contacts and upcoming events

            Output EXACTLY this format and nothing else:
            {{"skill": "contacts.read", "params": {{}}}}

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
    