from lib.database import Database
from shared.embedding_service import EmbeddingService

class MemoryService:

    def __init__(self):
        self.db = Database(app_name="ollama")
        self.embedding_service = EmbeddingService()


    def store(self, text: str, manager: str = "admin") -> None:
        embedding = self.embedding_service.embed(text)
        
        data = {
            "content": text,
            "embedding": embedding,
            "manager": manager
                }
        self.db.insert_data_to_table(table_name="la_memory_vectors", data=data)
        
        return
    
    def retrieve(self, text: str, manager: str = "admin", match_count: int = 5) -> list[str]:
        embedding = self.embedding_service.embed(text)

        data = {
            "query_embedding": embedding,
            "match_manager": manager,
            "match_count": match_count
        }
        results = self.db.match_memories(**data)
        return results






# if __name__ == "__main__":
#     memory_service = MemoryService()
#     memory_service.retrieve("This is a test memory.")  