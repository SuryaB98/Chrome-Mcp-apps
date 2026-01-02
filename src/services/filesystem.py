"""Filesystem operations service."""
import os
from pathlib import Path
import anyio
import logging
from src.config import settings
from src.services.security import is_safe_path

logger = logging.getLogger(__name__)

def _list_files_sync() -> list[str]:
    """Blocking helper to walk the directory tree."""
    files = []
    try:
        for root, _, filenames in os.walk(settings.FILES_DIR):
            for filename in filenames:
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(settings.FILES_DIR)
                files.append(str(rel_path))
        logger.info(f"Listed {len(files)} files from sandbox")
    except Exception as e:
        logger.error(f"Error listing files: {e}")
    return files

async def list_files() -> str:
    """
    Recursively list all allowed files in the root directory (Async).
    
    Returns:
        Newline-separated list of file paths
    """
    files = await anyio.to_thread.run_sync(_list_files_sync)
    return "\n".join(files) if files else "No files found."

async def read_file_content(path: str) -> str:
    """
    Read content of a file (safe types only, Async).
    
    Args:
        path: Relative path to the file
        
    Returns:
        File content or error message
        
    Security:
        - Validates path is within sandbox
        - Checks file extension whitelist
        - Enforces size limits
    """
    # Security check - use relative path
    path_obj = Path(path)
    if not is_safe_path(path_obj):
        logger.warning(f"Rejected file read attempt: {path}")
        return "Error: Access denied. Path is outside the sandbox."
    
    target_path = settings.FILES_DIR / path
    
    # Existence check
    if not target_path.exists():
        logger.info(f"File not found: {path}")
        return "Error: File not found."
    
    if not target_path.is_file():
        logger.warning(f"Attempted to read non-file: {path}")
        return "Error: Path is not a file."

    # Extension validation
    if target_path.suffix not in settings.ALLOWED_EXTENSIONS:
        logger.warning(f"Rejected unsupported file type: {path} ({target_path.suffix})")
        return f"Error: Unsupported file type '{target_path.suffix}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"

    # Size check
    MAX_SIZE = settings.MAX_FILE_SIZE_KB * 1024
    file_size = target_path.stat().st_size
    if file_size > MAX_SIZE:
        logger.warning(f"File too large: {path} ({file_size} bytes)")
        return f"Error: File too large ({file_size // 1024}KB > {settings.MAX_FILE_SIZE_KB}KB)."

    # Read content in thread
    try:
        content = await anyio.to_thread.run_sync(
            lambda: target_path.read_text(encoding='utf-8')
        )
        logger.info(f"Successfully read file: {path} ({len(content)} chars)")
        return content
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading {path}: {e}")
        return "Error: File encoding is not UTF-8."
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return f"Error reading file: {str(e)}"
