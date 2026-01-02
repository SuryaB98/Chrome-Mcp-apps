from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import logging

# Get project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Application Configuration.
    Reads from environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"), 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Info
    APP_NAME: str = "Chrome-MCP-Apps"
    APP_VERSION: str = "1.0.0"
    
    # Security: File Sandbox
    FILES_DIR: Path = Field(
        default=Path("./files"),
        description="Root directory for local file operations. Must exist."
    )
    
    # File Operation Limits
    MAX_FILE_SIZE_KB: int = Field(
        default=50,
        description="Maximum file size in KB for read operations"
    )
    
    ALLOWED_EXTENSIONS: set[str] = Field(
        default={'.txt', '.md', '.py'},
        description="Allowed file extensions for read operations"
    )

    # API Keys
    TAVILY_API_KEY: str = Field(
        ...,  # Required field
        description="API Key for Tavily Search Service. Get one at tavily.com"
    )
    
    # Research Settings
    DEFAULT_SEARCH_LIMIT: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Default number of search results"
    )
    
    HTTP_TIMEOUT: int = Field(
        default=10,
        description="HTTP request timeout in seconds"
    )

    @field_validator('FILES_DIR')
    @classmethod
    def resolve_files_dir(cls, v: Path) -> Path:
        """Resolve FILES_DIR relative to project root and create if needed."""
        if not v.is_absolute():
            v = PROJECT_ROOT / v
        v = v.resolve()
        v.mkdir(parents=True, exist_ok=True)
        logger.info(f"Files directory: {v}")
        return v
    
    @field_validator('TAVILY_API_KEY')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or v == "tvly-placeholder":
            logger.warning("Using placeholder Tavily API key - replace with real key for production")
        return v

# Singleton Instance
settings = Settings()
logger.info(f"Configuration loaded: {settings.APP_NAME} v{settings.APP_VERSION}")
