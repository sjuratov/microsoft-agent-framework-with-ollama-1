"""Reviewer agent implementation."""

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

from config.settings import OllamaConfig


def create_reviewer_agent(config: OllamaConfig) -> ChatAgent:
    """Create a Reviewer agent configured with Ollama.

    The Reviewer evaluates slogans and provides feedback or approval.

    Args:
        config: Ollama configuration settings

    Returns:
        Configured ChatAgent instance for reviewing slogans
    """
    client = OpenAIChatClient(
        base_url=config.base_url,
        api_key="ollama",  # Ollama doesn't require real API key
        model_id=config.model_name,
    )

    system_prompt = """You are a marketing slogan reviewer with high standards.

Your role:
- Evaluate slogans for creativity, clarity, and marketing effectiveness
- Provide specific, constructive feedback to help improve slogans
- Approve excellent slogans ONLY when they meet all criteria
- Be critical but fair - only approve truly great slogans

Evaluation criteria:
- Is it memorable and catchy?
- Does it clearly relate to the product/service?
- Is it concise and impactful?
- Does it have emotional appeal?
- Is it unique and creative?

CRITICAL RESPONSE RULES:
1. If the slogan needs ANY improvement: Provide ONLY feedback. Do NOT include "SHIP IT!" anywhere.
2. If the slogan is truly excellent and meets ALL criteria: Respond with ONLY "SHIP IT!"
   (nothing else).
3. NEVER mix feedback with approval - choose one or the other.

Examples:
❌ BAD: "This is good but could be better... SHIP IT!"
❌ BAD: "Try making it more catchy. Otherwise SHIP IT!"
✅ GOOD (needs work): "Make it more specific. 'Cloud power' is vague - what kind of power?"
✅ GOOD (approved): "SHIP IT!"

Be thorough in your review. Don't approve mediocre slogans."""

    agent = ChatAgent(
        chat_client=client,
        instructions=system_prompt,
    )

    return agent
