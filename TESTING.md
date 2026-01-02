# Manual Testing Guide for Chrome-MCP-Apps

This guide walks you through manually testing all features of the MCP server.

## Prerequisites

1. Virtual environment activated:
```powershell
.\venv\Scripts\activate
```

2. Ensure you're in the project directory:
```powershell
cd d:\Surya\Business\Tech\Chrome-MCP\source_code\Chrome-Mcp-apps
```

---

## Method 1: Using MCP Inspector (Recommended)

The MCP Inspector provides a visual interface to test all tools.

### Start the Inspector

```powershell
npx @modelcontextprotocol/inspector python main.py
```

**What happens:**
- Opens a web interface at `http://localhost:5173`
- Shows all available tools
- Allows interactive testing

### Testing Each Tool

#### 1. Test `heartbeat`
- Click on "heartbeat" tool
- Click "Run"
- **Expected:** `"Chrome-MCP-Apps v1.0.0 - Server is alive"`

#### 2. Test `list_files`
- Click on "list_files" tool
- Click "Run"
- **Expected:** List of files in the `files/` directory (e.g., `test.txt`)

#### 3. Test `read_file_content`
- Click on "read_file_content" tool
- Enter parameter: `path = "test.txt"`
- Click "Run"
- **Expected:** Content of the file

**Try security tests:**
- Path: `"../README.md"` → Should return "Error: Access denied"
- Path: `"C:/Windows/System32/drivers/etc/hosts"` → Should return "Error: Access denied"

#### 4. Test `search_web`
- Click on "search_web" tool
- Enter parameters:
  - `query = "Python 3.12 new features"`
  - `max_results = 3`
- Click "Run"
- **Expected:** Formatted search results with titles, URLs, and content

**Note:** This requires a valid Tavily API key in `.env`

#### 5. Test `fetch_url_content`
- Click on "fetch_url_content" tool
- Enter parameter: `url = "https://www.python.org"`
- Click "Run"
- **Expected:** Cleaned text content from the page

---

## Method 2: Direct Python Testing

Test individual functions directly from Python.

### Test 1: Configuration

```powershell
python -c "from src.config import settings; print(f'App: {settings.APP_NAME}'); print(f'Version: {settings.APP_VERSION}'); print(f'Sandbox: {settings.FILES_DIR}')"
```

**Expected output:**
```
App: Chrome-MCP-Apps
Version: 1.0.0
Sandbox: D:\Surya\Business\Tech\Chrome-MCP\source_code\Chrome-Mcp-apps\files
```

### Test 2: Security Service

```powershell
python -c "from pathlib import Path; from src.services.security import is_safe_path; print('Relative path:', is_safe_path(Path('test.txt'))); print('Absolute path:', is_safe_path(Path('C:/Windows'))); print('Traversal:', is_safe_path(Path('../etc')))"
```

**Expected output:**
```
Relative path: True
Absolute path: False
Traversal: False
```

### Test 3: File Operations

Create a test file first:
```powershell
echo "Hello from manual test" > files\manual_test.txt
```

Then test reading:
```powershell
python -c "import asyncio; from src.services.filesystem import read_file_content; print(asyncio.run(read_file_content('manual_test.txt')))"
```

**Expected output:**
```
Hello from manual test
```

### Test 4: List Files

```powershell
python -c "import asyncio; from src.services.filesystem import list_files; print(asyncio.run(list_files()))"
```

**Expected output:**
```
test.txt
manual_test.txt
```

---

## Method 3: Using pytest (Automated)

Run the full test suite:

```powershell
pytest tests/test_server.py -v
```

**Expected output:**
```
13 passed in 0.6s
```

Run specific tests:
```powershell
# Test only security
pytest tests/test_server.py::test_security_logic -v

# Test only file operations
pytest tests/test_server.py::test_read_file_content -v
```

---

## Method 4: Integration Test Script

Create a comprehensive test script:

```powershell
# Save this as test_integration.py
python -c @"
import asyncio
from src.server import heartbeat, list_files, read_file_content
from src.config import settings

async def test_all():
    print('=== Integration Test ===\n')
    
    # Test 1: Heartbeat
    print('1. Testing heartbeat...')
    result = heartbeat()
    print(f'   ✓ {result}\n')
    
    # Test 2: List files
    print('2. Testing list_files...')
    files = await list_files()
    print(f'   ✓ Found files:\n{files}\n')
    
    # Test 3: Read file
    print('3. Testing read_file_content...')
    content = await read_file_content('test.txt')
    print(f'   ✓ Content: {content[:50]}...\n')
    
    # Test 4: Security (should fail)
    print('4. Testing security (should deny)...')
    denied = await read_file_content('../README.md')
    print(f'   ✓ {denied}\n')
    
    print('=== All Tests Passed ===')

asyncio.run(test_all())
"@
```

---

## Common Issues & Solutions

### Issue 1: "Module not found"
**Solution:**
```powershell
# Ensure you're in the project directory
cd d:\Surya\Business\Tech\Chrome-MCP\source_code\Chrome-Mcp-apps

# Activate virtual environment
.\venv\Scripts\activate
```

### Issue 2: "Tavily API key error"
**Solution:**
```powershell
# Edit .env file and add your real key
notepad .env
# Change: TAVILY_API_KEY=your_actual_key_here
```

### Issue 3: "No files found"
**Solution:**
```powershell
# Create a test file
echo "Test content" > files\test.txt
```

---

## Quick Verification Checklist

Run these commands in order:

```powershell
# 1. Check imports
python -c "from src.server import mcp; print('✓ Imports OK')"

# 2. Check configuration
python -c "from src.config import settings; print(f'✓ Config OK: {settings.APP_NAME}')"

# 3. Run tests
pytest tests/ -v

# 4. Start inspector
npx @modelcontextprotocol/inspector python main.py
```

If all 4 steps succeed, your server is **fully functional**! 🎉

---

## Expected Behavior Summary

| Tool | Input | Expected Output |
|------|-------|----------------|
| `heartbeat` | None | `"Chrome-MCP-Apps v1.0.0 - Server is alive"` |
| `list_files` | None | List of files in sandbox |
| `read_file_content` | `"test.txt"` | File content |
| `read_file_content` | `"../etc"` | `"Error: Access denied"` |
| `search_web` | `"Python"` | Search results (needs API key) |
| `fetch_url_content` | `"https://python.org"` | Cleaned page text |

---

## Next Steps

Once manual testing is complete:
1. ✅ Replace placeholder API key with real one
2. ✅ Add more test files to `files/` directory
3. ✅ Integrate with your AI application
4. ✅ Monitor logs for any issues

**Logs Location:** Console output shows all operations with timestamps
