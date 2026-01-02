"""MCP Server definition and tool registration."""
import logging
from mcp.server.fastmcp import FastMCP
from src.config import settings
from src.services import filesystem, research

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(settings.APP_NAME)

logger.info(f"Initializing {settings.APP_NAME} v{settings.APP_VERSION}")

# ============================================================================
# HEALTH & DIAGNOSTICS
# ============================================================================

@mcp.tool()
def heartbeat() -> str:
    """
    Health check endpoint.
    
    Returns:
        Status message confirming server is alive
    """
    return f"{settings.APP_NAME} v{settings.APP_VERSION} - Server is alive"

# ============================================================================
# FILESYSTEM OPERATIONS
# ============================================================================

@mcp.tool()
async def list_files() -> str:
    """
    List all files in the sandboxed directory.
    
    Returns:
        Newline-separated list of file paths relative to sandbox root
        
    Security:
        Only files within the configured sandbox are accessible
    """
    return await filesystem.list_files()

@mcp.tool()
async def read_file_content(path: str) -> str:
    """
    Read the content of a file from the sandbox.
    
    Args:
        path: Relative path to the file (e.g., 'notes.txt' or 'docs/readme.md')
        
    Returns:
        File content as UTF-8 text, or error message
        
    Security:
        - Path must be relative and within sandbox
        - Only allowed file types (.txt, .md, .py)
        - Size limit enforced (default 50KB)
        
    Examples:
        read_file_content("notes.txt")
        read_file_content("project/README.md")
    """
    return await filesystem.read_file_content(path)

# ============================================================================
# WEB RESEARCH
# ============================================================================

@mcp.tool()
async def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web using Tavily AI-powered search.
    
    Args:
        query: Search query (e.g., "latest Python version", "how to use async in Python")
        max_results: Maximum number of results to return (1-10, default: 5)
        
    Returns:
        Formatted search results with titles, URLs, and AI-generated answer
        
    Features:
        - AI-optimized search results
        - Includes direct answer when available
        - Clean, structured content
        
    Examples:
        search_web("Python 3.12 new features")
        search_web("best practices for async programming", max_results=3)
    """
    return await research.search_tavily(query, max_results)

@mcp.tool()
async def fetch_url_content(url: str) -> str:
    """
    Fetch and extract text content from a specific URL.
    
    Args:
        url: Full URL to fetch (must include http:// or https://)
        
    Returns:
        Extracted text content from the page, or error message
        
    Features:
        - Removes navigation, scripts, and styling
        - Returns clean, readable text
        - Respects timeout limits
        
    Examples:
        fetch_url_content("https://docs.python.org/3/whatsnew/3.12.html")
    """
    return await research.fetch_page_content(url)

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} MCP Server...")
    logger.info(f"Sandbox directory: {settings.FILES_DIR}")
    logger.info(f"Tools registered: heartbeat, list_files, read_file_content, search_web, fetch_url_content")
    mcp.run(transport='stdio')
