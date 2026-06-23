from groq import AsyncGroq
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

MODEL_NAME = "llama-3.3-70b-versatile"


class GroqSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: SecretStr


class SummarizerError(RuntimeError):
    """Raised when the narrative summarizer cannot produce a response."""


async def call_groq(system_prompt: str, user_prompt: str) -> str:
    try:
        api_key = GroqSettings().groq_api_key.get_secret_value()
        client = AsyncGroq(api_key=api_key)
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Groq returned an empty response")
        return content
    except Exception as exc:
        raise SummarizerError(
            f"Failed to generate profile summary with Groq "
            f"({type(exc).__name__}): {exc}"
        ) from exc
