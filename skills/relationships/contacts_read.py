from pydantic import BaseModel

from lib.database import Database

from lib.log import logger
from skills.base import SkillBase, SkillResult

log = logger.get_logger()

class Person(BaseModel):
    id: str
    full_name: str
    nickname: str | None = None
    relationship_type: str | None = None
    importance_level: int
    email: str | None = None
    phone : str | None = None 
    city: str | None = None

class ContactsRead(SkillBase):
    def __init__(self):
        super().__init__()
        self.db = Database(app_name="ollama")
        self.lookup_cache = self._get_lookup_map()
        self.rel_people_lookup = self._get_rel_people_lookup()

    @property
    def name(self) -> str:
        return "contacts.read"
    
    def execute(self, **kwargs) -> SkillResult:
        people = self._get_relation_people_data()
        events = self._get_relation_event()
        
        return SkillResult(success=True, data={
            "people": people,
            "upcoming_events": events
        })

    def _get_lookup_map(self):
        table_name = "shared_people"

        response = self.db.get_data_from_table(table_name=table_name)

        if response is None:
            log.error("Database returned None")
            return "Database returned None"
        
        objs = [Person(**person) for person in response]
        
        return {person.id: person for person in objs}
        
    def _get_relation_people_data(self) -> list:
        table_name = "rel_people"

        response = self.db.get_data_from_table(table_name=table_name)

        if response is None:
            log.error("Database returned None")
            return "Database returned None"
        
        people_data = []

        for relation in response:
            shared_person_id = relation.get("shared_people_id")
            if shared_person_id is None:
                log.warning(f"Relation {relation['id']} does not have shared_person_id")
                continue
            person_obj = self.lookup_cache.get(shared_person_id)
            if person_obj is None:
                log.warning(f"Shared person ID {shared_person_id} not found in lookup cache")
                continue
            person_name = person_obj.full_name
            relation_type = person_obj.relationship_type or "unknown"
            importance = person_obj.importance_level or "unknown"
            
            people_data.append({
                "name": person_name,
                "relation_type": relation_type,
                "importance": importance
            })

        return people_data
    
    def _get_rel_people_lookup(self) -> dict:
        response = self.db.get_data_from_table(table_name="rel_people")
        if not response:
            return {}
        # maps rel_people.id → shared_people_id
        return {row["id"]: row["shared_people_id"] for row in response}

    def _get_relation_event(self):
        table_name = "rel_events"

        response = self.db.get_data_from_table(table_name=table_name)

        if response is None:
            log.error("Database returned None")
            return "Database returned None"
        
        people_data = []
        
        for event in response:
            person_id = event.get("person_id")
            shared_people_id = self.rel_people_lookup.get(person_id)
            person = self.lookup_cache.get(shared_people_id)
            person_name = person.full_name if person else "Unknown"
            event_type = event.get("event_type", "unknown")
            event_date = event.get("event_date", "unknown")
            people_data.append({
                "name": person_name,
                "event_type": event_type,
                "event_date": event_date
            })

        return people_data
            

if __name__ == "__main__":
    skill = ContactsRead()
    result = skill.execute()
    print(result)