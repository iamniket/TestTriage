import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_client(provider: str = "groq"):
    """Returns an OpenAI-compatible client and default model for the chosen provider."""
    if provider == "groq":
        return OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        ), "llama-3.3-70b-versatile"

    if provider == "github":
        return OpenAI(
            api_key=os.getenv("GITHUB_TOKEN"),
            base_url="https://models.github.ai/inference"
        ), "openai/gpt-4.1"

    if provider == "gemini":
        return OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ), "gemini-2.5-flash"

    raise ValueError(f"Unknown provider: {provider}")