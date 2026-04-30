from admin.intent_classifier import IntentClassifier
from managers.base import BaseManager, ManagerRequest
from shared.memory_service import MemoryService
from shared.ollama_service import OllamaService
from lib.log import logger

log = logger.get_logger()


class AdminOrchestrator:
    def __init__(self, managers: dict[str, BaseManager], ollama: OllamaService, memory: MemoryService):
        self.ollama = ollama
        self.memory = memory
        self.managers = managers
        self.classifier = IntentClassifier(ollama)

    def process(self, message: str) -> str:
        classifier = self.classifier.classify(message)
        domain = classifier.get("domain", "unknown")
        log.info(f"Intent: {domain}")

        if domain in ("multi", "unknown"):
            return self.ollama.generate(message)
        
        manager = self.managers.get(domain)
        if not manager:
            log.warning(f"No manager found for domain: {domain}")
            return "Sorry, I couldn't process your request."
        
        request = ManagerRequest(task=message, context={})
        response = manager.process(request)
    
        if not response:
            return "Manager returned no response"
        return response.summary
            

if __name__ == "__main__":
    managers = {
        #only for testing, replace with actual manager instances
        "life_admin": "LifeAdminManager()",
        "finance": "FinanceManager()",
    }
    orchesterator = AdminOrchestrator(managers=managers, ollama=OllamaService(), memory=MemoryService())

    orchesterator.process("I need help managing my schedule and finances.")