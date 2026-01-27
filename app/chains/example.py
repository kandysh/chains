"""Example LangChain chain."""

from langchain import PromptTemplate
from app.config import get_settings


settings = get_settings()


async def example_chain(input_text: str) -> str:
    """
    Example async chain function.

    Add your LangChain logic here.
    """
    # TODO: Implement chain logic
    return f"Processed: {input_text}"
