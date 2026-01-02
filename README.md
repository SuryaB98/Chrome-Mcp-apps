# Chrome-MCP-Apps - Production MCP Server

[![Tests](https://img.shields.io/badge/tests-13%20passed-success)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

A production-ready Model Context Protocol (MCP) server providing AI agents with secure file system access and intelligent web research capabilities.

## 🎯 Features

### 🔒 Secure File Operations
- **Sandboxed Access**: All file operations restricted to configured directory
- **Path Validation**: Multi-layer security preventing directory traversal
- **Type Restrictions**: Whitelist-based file extension filtering
- **Size Limits**: Configurable maximum file size enforcement
- **Async I/O**: Non-blocking operations for high concurrency

### 🔍 AI-Powered Web Research
- **Tavily Integration**: Production-grade AI search with clean results
- **Content Extraction**: Intelligent web page parsing and cleaning
- **Rate Limiting**: Built-in protection and timeout handling
- **Error Recovery**: Comprehensive error handling with fallbacks

### 🏗️ Production Architecture
- **Modular Design**: Clean separation of concerns (services, config, tools)
- **Type Safety**: Pydantic-based configuration with validation
- **Logging**: Structured logging for monitoring and debugging
- **Testing**: Comprehensive test suite with 13+ test cases
- **Documentation**: Extensive inline and API documentation

## 📁 Project Structure

```
Chrome-Mcp-apps/
├── src/                          # Source code
│   ├── config.py                 # Configuration (Pydantic Settings)
│   ├── server.py                 # MCP server & tool definitions
│   ├── services/                 # Business logic layer
│   │   ├── security.py           # Path validation & sandbox
│   │   ├── filesystem.py         # File operations
│   │   └── research.py           # Web search & extraction
│   └── tools/                    # (Reserved for extensions)
├── tests/                        # Test suite (pytest)
│   └── test_server.py
├── files/                        # Sandboxed file storage
├── main.py                       # Entry point
├── .env                          # Environment configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Tavily API key ([Get one free](https://tavily.com))

### Installation

1. **Clone or download the project**
```bash
cd Chrome-Mcp-apps
```

2. **Create virtual environment**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Edit .env file
TAVILY_API_KEY=your_actual_key_here
```

5. **Run the server**
```bash
python main.py
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python main.py
```

This opens a web interface at `http://localhost:5173` where you can test all tools.

## 🛠️ Available Tools

### 1. `heartbeat()`
Health check endpoint.
```
Returns: "Chrome-MCP-Apps v1.0.0 - Server is alive"
```

### 2. `list_files()`
List all files in the sandbox.
```
Returns: Newline-separated list of file paths
Example: "notes.txt\ndocs/readme.md\nproject/data.py"
```

### 3. `read_file_content(path: str)`
Read file content from sandbox.
```
Args:
  path: Relative path (e.g., "notes.txt", "docs/readme.md")
  
Returns: File content as UTF-8 text

Security:
  - Only .txt, .md, .py files allowed
  - 50KB size limit (configurable)
  - Path must be within sandbox
```

### 4. `search_web(query: str, max_results: int = 5)`
AI-powered web search via Tavily.
```
Args:
  query: Search query
  max_results: Number of results (1-10)
  
Returns: Formatted results with AI-generated answer

Example:
  search_web("Python 3.12 new features", max_results=3)
```

### 5. `fetch_url_content(url: str)`
Extract clean text from a URL.
```
Args:
  url: Full URL (must include http:// or https://)
  
Returns: Cleaned text content

Example:
  fetch_url_content("https://docs.python.org/3/whatsnew/3.12.html")
```

## ⚙️ Configuration

All configuration is managed through `.env` file and validated by Pydantic:

```env
# Required
TAVILY_API_KEY=tvly-your-key-here

# Optional (defaults shown)
FILES_DIR=./files
MAX_FILE_SIZE_KB=50
DEFAULT_SEARCH_LIMIT=5
HTTP_TIMEOUT=10
```

### Configuration Options

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `TAVILY_API_KEY` | string | *required* | Tavily API key |
| `FILES_DIR` | path | `./files` | Sandbox directory |
| `MAX_FILE_SIZE_KB` | int | `50` | Max file size for reads |
| `DEFAULT_SEARCH_LIMIT` | int | `5` | Default search results |
| `HTTP_TIMEOUT` | int | `10` | HTTP timeout (seconds) |

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## 🔐 Security

### Sandbox Enforcement
- All file paths validated against configured `FILES_DIR`
- Absolute paths rejected
- Directory traversal (`../`) blocked
- Symlinks resolved and validated

### Input Validation
- File extensions whitelist
- Size limits enforced
- Path sanitization
- Type checking via Pydantic

### Logging
All security events logged:
- Path validation failures
- Access denied attempts
- File operation errors
- API errors

## 📊 Performance

- **Async I/O**: Non-blocking file and network operations
- **Thread Pool**: CPU-bound tasks offloaded to threads
- **Connection Pooling**: HTTP client reuses connections
- **Timeout Protection**: All network calls have timeouts

## 🔧 Development

### Adding New Tools

1. Create service function in `src/services/`
2. Add tool definition in `src/server.py`
3. Write tests in `tests/test_server.py`
4. Update documentation

Example:
```python
# src/services/my_service.py
async def my_function(param: str) -> str:
    # Implementation
    return result

# src/server.py
@mcp.tool()
async def my_tool(param: str) -> str:
    """Tool description."""
    return await my_service.my_function(param)
```

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Log important events

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For issues and questions:
- GitHub Issues: [Report a bug]
- Documentation: See inline code documentation

## 🎓 Learn More

- [MCP Documentation](https://modelcontextprotocol.io)
- [Tavily API](https://docs.tavily.com)
- [FastMCP](https://github.com/jlowin/fastmcp)

---

**Built with ❤️ for production use**
