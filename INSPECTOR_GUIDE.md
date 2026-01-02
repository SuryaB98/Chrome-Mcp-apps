# MCP Inspector Testing Guide

## Quick Start (3 Steps)

### Step 1: Stop Any Running Inspector
```powershell
# Press Ctrl+C in the terminal where inspector is running
# Or close the terminal window
```

### Step 2: Start Fresh Inspector
```powershell
npx @modelcontextprotocol/inspector python main.py
```

**Important:** Use `main.py`, NOT `server.py` (server.py was deleted during refactoring)

### Step 3: Open Browser
The inspector will automatically open at: `http://localhost:5173`

If it doesn't open automatically:
1. Look for the URL in the terminal output
2. Copy and paste it into your browser

---

## What You'll See

### Inspector Interface

```
┌─────────────────────────────────────────┐
│  MCP Inspector                          │
├─────────────────────────────────────────┤
│  Server: Chrome-MCP-Apps                │
│  Status: ● Connected                    │
├─────────────────────────────────────────┤
│  Tools (5):                             │
│  ├─ heartbeat                           │
│  ├─ list_files                          │
│  ├─ read_file_content                   │
│  ├─ search_web                          │
│  └─ fetch_url_content                   │
└─────────────────────────────────────────┘
```

---

## Testing Each Tool

### 1. Test `heartbeat`
**Purpose:** Verify server is running

**Steps:**
1. Click "heartbeat" in the tools list
2. Click "Execute" or "Run"

**Expected Result:**
```
"Chrome-MCP-Apps v1.0.0 - Server is alive"
```

---

### 2. Test `list_files`
**Purpose:** List files in sandbox

**Steps:**
1. Click "list_files"
2. Click "Execute"

**Expected Result:**
```
test.txt
manual_test.txt
```

---

### 3. Test `read_file_content`
**Purpose:** Read a file with security validation

**Steps:**
1. Click "read_file_content"
2. In the parameters section, enter:
   ```json
   {
     "path": "test.txt"
   }
   ```
3. Click "Execute"

**Expected Result:**
```
Hello from manual test
```

**Security Test:**
Try reading outside sandbox:
```json
{
  "path": "../README.md"
}
```

**Expected Result:**
```
Error: Access denied. Path is outside the sandbox.
```

---

### 4. Test `search_web` (Requires API Key)
**Purpose:** Search the web using Tavily

**Prerequisites:**
1. Add your Tavily API key to `.env`:
   ```
   TAVILY_API_KEY=tvly-your-actual-key
   ```
2. Restart the inspector

**Steps:**
1. Click "search_web"
2. Enter parameters:
   ```json
   {
     "query": "What's the latest C# version?",
     "max_results": 3
   }
   ```
3. Click "Execute"

**Expected Result:**
```
**Answer**: C# 12 was released in November 2023...

**Result 1**
Title: C# 12 Features
URL: https://learn.microsoft.com/...
Content: C# 12 introduces primary constructors...

---

**Result 2**
...
```

**If you see "Tavily client not installed":**
- The package is installed, but you need a real API key
- Get one free at: https://tavily.com

---

### 5. Test `fetch_url_content`
**Purpose:** Extract clean text from a URL

**Steps:**
1. Click "fetch_url_content"
2. Enter parameters:
   ```json
   {
     "url": "https://www.python.org"
   }
   ```
3. Click "Execute"

**Expected Result:**
```
Python
Welcome to Python.org
Get Started
Whether you're new to programming or an experienced developer...
[Clean text content, no HTML tags]
```

---

## Troubleshooting

### Problem: "Port is in use"
**Solution:**
```powershell
# Option 1: Find and kill the process
Get-Process -Name node | Stop-Process -Force

# Option 2: Use a different port
npx @modelcontextprotocol/inspector --port 6278 python main.py
```

### Problem: "Cannot find main.py"
**Solution:**
```powershell
# Make sure you're in the project directory
cd d:\Surya\Business\Tech\Chrome-MCP\source_code\Chrome-Mcp-apps

# Verify main.py exists
dir main.py
```

### Problem: Inspector shows "Disconnected"
**Solution:**
1. Check the terminal for error messages
2. Ensure virtual environment is activated:
   ```powershell
   .\venv\Scripts\activate
   ```
3. Restart inspector

### Problem: "Module not found" errors
**Solution:**
```powershell
# Reinstall dependencies
.\venv\Scripts\pip install -r requirements.txt
```

---

## Advanced Testing

### Test with Custom Files

1. Create a test file:
   ```powershell
   echo "This is a test document" > files\document.txt
   ```

2. Test reading it:
   - Tool: `read_file_content`
   - Path: `"document.txt"`

### Test Error Handling

1. **Non-existent file:**
   - Path: `"does_not_exist.txt"`
   - Expected: `"Error: File not found"`

2. **Wrong extension:**
   ```powershell
   echo "test" > files\test.exe
   ```
   - Path: `"test.exe"`
   - Expected: `"Error: Unsupported file type"`

3. **Large file:**
   ```powershell
   # Create 100KB file
   $content = "x" * 102400
   Set-Content -Path "files\large.txt" -Value $content
   ```
   - Path: `"large.txt"`
   - Expected: `"Error: File too large"`

---

## Monitoring Logs

While testing, watch the terminal where inspector is running. You'll see:

```
2026-01-02 15:37:00 - src.config - INFO - Files directory: ...
2026-01-02 15:37:05 - src.services.filesystem - INFO - Listed 2 files from sandbox
2026-01-02 15:37:10 - src.services.filesystem - INFO - Successfully read file: test.txt (23 chars)
```

This helps you understand what's happening behind the scenes.

---

## Quick Reference

| Tool | Parameters | Example |
|------|------------|---------|
| `heartbeat` | None | - |
| `list_files` | None | - |
| `read_file_content` | `path` | `{"path": "test.txt"}` |
| `search_web` | `query`, `max_results` | `{"query": "Python", "max_results": 5}` |
| `fetch_url_content` | `url` | `{"url": "https://python.org"}` |

---

## Success Checklist

- [ ] Inspector starts without errors
- [ ] All 5 tools are visible
- [ ] `heartbeat` returns version info
- [ ] `list_files` shows files
- [ ] `read_file_content` reads files
- [ ] Security blocks `../` paths
- [ ] `fetch_url_content` returns clean text
- [ ] `search_web` works (with API key)

Once all items are checked, your server is **fully functional**! 🎉
