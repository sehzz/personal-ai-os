from pydantic import BaseModel

from lib.environment import get_conf_for


class Settings(BaseModel):
    # Ollama
    ollama_base_url: str
    ollama_model: str

    # Supabase
    db_url: str
    db_api_key: str


def test():
    conf = get_conf_for("ollama")
    settings = Settings(**conf)
    print(settings)


if __name__ == "__main__":
    test()