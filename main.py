"""Main entry point for the MCP server."""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.server import mcp

if __name__ == "__main__":
    mcp.run(transport='stdio')
