from lib.connectors import URLCaller
from lib.environment import get_conf_for

class EmbeddingService:
    def __init__(self):
        conf = get_conf_for("ollama")
        self.caller = URLCaller()
        self.base_url = conf["ollama_base_url"]
        self.model = conf["ollama_embed_model"]

    def embed(self, text: str) -> list[float]:
        url = f"{self.base_url}/api/embeddings"

        payload = {
            "model": self.model,
            "prompt": text
        }

        response = self.caller.perform_single_call(url=url, verb="POST", json=payload)

        if response.status != 200:
            raise Exception(f"Ollama API error: {response.status} - {response.json}")
        
        api_response = response.json

        embed_vector = api_response.get("embedding", [])

        return embed_vector
                
if __name__ == "__main__":
    embedding_service = EmbeddingService()
    text = "What is the capital of France?"
    embedding = embedding_service.embed(text)
    print(f"Embedding for '{text}': {embedding}")