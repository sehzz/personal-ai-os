



def build_prompt(message: str, memories: list[str], mode: str = "chat"):
    prefix = "You must reply in maximum 2 sentences. No exceptions. Be direct.\n\n" if mode == "voice" else ""

    if not memories:
        return f"{prefix}{message}"
    
    prompt = f"{prefix}You are a helpful assistant. Use the following memories to answer the question.\n\n"
    for i, memory in enumerate(memories):
        prompt += f"Memory {i+1}: {memory}\n"
    prompt += f"User message: {message}\n"

    return prompt