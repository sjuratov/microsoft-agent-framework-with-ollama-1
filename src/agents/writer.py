"""Writer agent implementation."""

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

from config.settings import OllamaConfig


def create_writer_agent(config: OllamaConfig) -> ChatAgent:
    """Create a Writer agent configured with Ollama.
    
    The Writer generates creative slogans based on user input and reviewer feedback.
    
    Args:
        config: Ollama configuration settings
        
    Returns:
        Configured ChatAgent instance for writing slogans
    """
    client = OpenAIChatClient(
        base_url=config.base_url,
        api_key="ollama",  # Ollama doesn't require real API key
        model_id=config.model_name,
    )
    
    system_prompt = """You are a creative slogan writer for marketing campaigns.

Your role:
- Generate catchy, memorable slogans based on the user's product/service description
- Incorporate any feedback from the reviewer to improve your slogans
- Be creative, concise, and impactful
- Keep slogans under 100 characters when possible
- Focus on emotional appeal and memorability

When you receive feedback, carefully revise your slogan to address the reviewer's concerns while maintaining creativity.

Output only the slogan text, nothing else."""

    agent = ChatAgent(
        chat_client=client,
        instructions=system_prompt,
    )
    
    return agent
