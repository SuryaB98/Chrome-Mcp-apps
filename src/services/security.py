"""Security service for path validation and sandbox enforcement."""
from pathlib import Path
import logging
from src.config import settings

logger = logging.getLogger(__name__)

class SecurityViolation(Exception):
    """Raised when a security policy is violated."""
    pass

def is_safe_path(path: Path) -> bool:
    """
    Ensure the path is within the allowed FILES_DIR sandbox.
    
    Args:
        path: Path to validate (should be relative)
        
    Returns:
        True if path is safe to access, False otherwise
        
    Security Checks:
        1. Rejects absolute paths
        2. Validates path resolves within sandbox
        3. Prevents directory traversal attacks
    """
    # Check 1: Explicitly disallow absolute paths
    if path.is_absolute():
        logger.warning(f"Security: Rejected absolute path: {path}")
        return False
    
    # Check 2: Resolve and validate within sandbox    
    try:
        full_path = (settings.FILES_DIR / path).resolve()
        is_safe = full_path.is_relative_to(settings.FILES_DIR)
        
        if not is_safe:
            logger.warning(f"Security: Path escapes sandbox: {path} -> {full_path}")
        
        return is_safe
    except (ValueError, OSError) as e:
        logger.error(f"Security: Path validation error for {path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Security: Unexpected error validating {path}: {e}")
        return False
