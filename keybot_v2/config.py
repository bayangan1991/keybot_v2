from pydantic import BaseSettings, Field


class KeyBotSettings(BaseSettings):
    wait_period: int = Field(
        60, description="Wait time between successful claims in minutes"
    )


settings = KeyBotSettings()
