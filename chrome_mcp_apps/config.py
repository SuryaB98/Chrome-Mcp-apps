from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Application Configuration.
    Reads from environment variables or .env file.
    """
    model_config = SettingsConfigDict(

        
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Info
    APP_NAME: str = "Chrome-MCP-Apps"
    
    # Security: File Sandbox
    FILES_DIR: Path = Field(
        default=Path("./files"),
        description="Root directory for local file operations. Must exist."
    )

    # API Keys
    TAVILY_API_KEY: str = Field(
        ..., # ... means required
        description="API Key for Tavily Search Service. Get one at tavily.com"
    )

    def validate_sandbox(self):
        """Ensure sandbox directory exists."""
        self.FILES_DIR = self.FILES_DIR.resolve()
        self.FILES_DIR.mkdir(parents=True, exist_ok=True)

# Singleton Instance
settings = Settings()
settings.validate_sandbox()
