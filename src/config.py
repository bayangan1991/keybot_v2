from pydantic import BaseSettings, Field


class DatabaseSettings(BaseSettings):
    class Config(BaseSettings.Config):
        env_prefix = "DB_"

    url: str = "sqlite:///:memory:"
    echo: bool = False


class DiscordSettings(BaseSettings):
    class Config(BaseSettings.Config):
        env_prefix = "DISCORD_"

    wait_period: int = Field(
        60, description="Wait time between successful claims in minutes"
    )


class AppSettings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    discord: DiscordSettings = DiscordSettings()


settings = AppSettings()
