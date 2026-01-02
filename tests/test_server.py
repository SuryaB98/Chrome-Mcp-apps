"""Test suite for Chrome-MCP-Apps server."""
import pytest
import sys
import os
from pathlib import Path

# Ensure src code can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.security import is_safe_path
from src.services.filesystem import list_files, read_file_content
from src.config import settings
from src.server import heartbeat

FILES_DIR = settings.FILES_DIR

# ============================================================================
# HEALTH CHECKS
# ============================================================================

def test_heartbeat():
    """Verify heartbeat returns expected message."""
    result = heartbeat()
    assert "alive" in result.lower()
    assert settings.APP_NAME in result

# ============================================================================
# SECURITY TESTS
# ============================================================================

@pytest.mark.parametrize("path_str,expected", [
    ("test.txt", True),                  # Relative allowed
    ("subdir/test.txt", True),           # Subdir relative allowed
    ("../windows", False),               # Traversal blocked
    ("/", False),                        # Root blocked
    ("C:/Windows/System32", False),      # Absolute blocked
    (str(FILES_DIR / "test.txt"), False), # Absolute (even if valid) blocked by policy
])
def test_security_logic(path_str, expected):
    """Verify directory restriction logic."""
    p = Path(path_str)
    assert is_safe_path(p) == expected

# ============================================================================
# FILESYSTEM TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_list_files():
    """Verify listing files finds the test file."""
    # Ensure test file exists
    test_file = FILES_DIR / "test.txt"
    if not test_file.exists():
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("Test content", encoding="utf-8")

    result = await list_files()
    assert "test.txt" in result

@pytest.mark.asyncio
async def test_read_file_content():
    """Verify reading file content."""
    # Ensure test file with known content
    test_file = FILES_DIR / "test.txt"
    test_file.write_text("Hello Pytest", encoding="utf-8")

    content = await read_file_content("test.txt")
    assert "Hello Pytest" in content

@pytest.mark.asyncio
async def test_read_blocked_file():
    """Verify reading a blocked file returns error."""
    # Attempt to read parent directory (should fail)
    result = await read_file_content("../requirements.txt")
    assert "Error: Access denied" in result

@pytest.mark.asyncio
async def test_read_nonexistent_file():
    """Verify reading nonexistent file returns appropriate error."""
    result = await read_file_content("nonexistent_file.txt")
    assert "Error: File not found" in result

@pytest.mark.asyncio
async def test_read_unsupported_extension():
    """Verify unsupported file types are rejected."""
    # Create a .exe file (not in whitelist)
    test_file = FILES_DIR / "test.exe"
    test_file.write_bytes(b"fake exe")
    
    result = await read_file_content("test.exe")
    assert "Unsupported file type" in result
    
    # Cleanup
    test_file.unlink()

# ============================================================================
# RESEARCH TESTS (Mocked)
# ============================================================================

@pytest.mark.asyncio
async def test_search_web_mock(monkeypatch):
    """Test search_web with mocked Tavily client."""
    from src.services import research
    
    # Mock the Tavily client
    class MockTavilyClient:
        def __init__(self, api_key):
            pass
        
        def search(self, query, max_results, search_depth, include_answer, include_raw_content):
            return {
                'answer': 'Python 3.12 was released in October 2023',
                'results': [
                    {
                        'title': 'Python 3.12 Release',
                        'url': 'https://python.org',
                        'content': 'Python 3.12 introduces new features...'
                    }
                ]
            }
    
    # Patch the import
    import sys
    sys.modules['tavily'] = type(sys)('tavily')
    sys.modules['tavily'].TavilyClient = MockTavilyClient
    
    result = await research.search_tavily("Python 3.12", limit=1)
    assert "Python 3.12" in result
    assert "python.org" in result.lower()
