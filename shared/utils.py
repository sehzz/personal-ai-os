



def build_prompt(message: str, memories: list[str]):
    if not memories:
        return message
    
    prompt = "You are a helpful assistant. Use the following memories to answer the question.\n\n"
    for i, memory in enumerate(memories):
        prompt += f"Memory {i+1}: {memory}\n"
    prompt += f"User message: {message}\n"

    return prompt