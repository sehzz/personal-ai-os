

import json

from shared.ollama_service import OllamaService


class IntentClassifier:
    def __init__(self, ollama: OllamaService):
        self.ollama = ollama

    def classify(self, message: str) -> dict:
        prompt = f"""You are an intent classifier for a Personal AI OS. Classify the user message below.

        The available domains are:
        - life_admin: tasks, calendar, bills, subscriptions, deadlines, schedule, reminders
        - finance: money, spending, budget, transactions, investments, expenses, income
        - content: social media, posts, reels, analytics, content ideas, Instagram, TikTok
        - relationships: people, birthdays, anniversaries, friends, family, contacts
        - multi: the message spans more than one domain above
        - unknown: cannot be classified into any domain above

        Return ONLY a JSON object with these exact fields:
        - domain: one of [life_admin, finance, content, relationships, multi, unknown]
        - urgency: one of [immediate, scheduled, background]
        - type: one of [question, action, multi_domain, proactive_brief]

        No explanation. No markdown. JSON only.

        Message: {message}
"""
        response = self.ollama.generate(prompt)
        response = response.strip().strip("```json").strip("```").strip()
        
        return json.loads(response)
    

if __name__ == "__main__":
    ollama_service = OllamaService()
    classifier = IntentClassifier(ollama_service)

    test_message = "I need to book a flight for next week and also check my bank account balance."
    classification = classifier.classify(test_message)
    print(f"Classification: {classification}")