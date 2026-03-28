import json

from lib.connectors import URLCaller
from lib.environment import get_conf_for


class OllamaService():
    def __init__(self):
        conf = get_conf_for("ollama")
        self.caller = URLCaller()
        self.base_url = conf["ollama_base_url"]
        self.model = conf["ollama_model"]

    def generate(self, prompt: str) -> str:

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = self.caller.post_httpx(url=url, json=payload)

        if response.status != 200:
            raise Exception(f"Ollama API error: {response.status} - {response.json}")
        
        api_response = response.json

        return api_response.get("response", "")
    
    def generate_stream(self, prompt: str):

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        raw_stream = self.caller.stream_httpx(url=url, json=payload)

        for line in raw_stream:
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "response" in chunk:
                yield chunk["response"]




if __name__ == "__main__":
    ollama_service = OllamaService()
    response = ollama_service.generate_stream("What is the capital of France?")
    # print("=======================================")
    # print(f"Ollama response: {response}")
    for chunk in response:
        print(f"Chunk: {chunk}",flush=True)