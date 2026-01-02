"""Quick manual test script for Chrome-MCP-Apps."""
import asyncio
from src.server import heartbeat, list_files, read_file_content
from src.config import settings

async def main():
    print("=" * 60)
    print("CHROME-MCP-APPS MANUAL TEST")
    print("=" * 60)
    print()
    
    # Test 1: Configuration
    print("📋 Configuration:")
    print(f"   App Name: {settings.APP_NAME}")
    print(f"   Version: {settings.APP_VERSION}")
    print(f"   Sandbox: {settings.FILES_DIR}")
    print(f"   Max File Size: {settings.MAX_FILE_SIZE_KB}KB")
    print()
    
    # Test 2: Heartbeat
    print("💓 Testing heartbeat...")
    result = heartbeat()
    print(f"   ✓ {result}")
    print()
    
    # Test 3: List Files
    print("📁 Testing list_files...")
    files = await list_files()
    print(f"   ✓ Files in sandbox:")
    for line in files.split('\n'):
        print(f"      - {line}")
    print()
    
    # Test 4: Read File (if exists)
    print("📖 Testing read_file_content...")
    if "test.txt" in files:
        content = await read_file_content("test.txt")
        if not content.startswith("Error"):
            print(f"   ✓ Successfully read test.txt ({len(content)} chars)")
            print(f"   Preview: {content[:100]}...")
        else:
            print(f"   ✗ {content}")
    else:
        print("   ⚠ No test.txt found - creating one...")
        test_file = settings.FILES_DIR / "test.txt"
        test_file.write_text("Hello from manual test!", encoding="utf-8")
        print("   ✓ Created test.txt")
    print()
    
    # Test 5: Security Test
    print("🔒 Testing security (should deny)...")
    denied = await read_file_content("../README.md")
    if "Access denied" in denied:
        print(f"   ✓ Security working: {denied}")
    else:
        print(f"   ✗ Security failed: {denied}")
    print()
    
    print("=" * 60)
    print("✅ ALL MANUAL TESTS COMPLETED")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run full test suite: pytest tests/ -v")
    print("2. Start inspector: npx @modelcontextprotocol/inspector python main.py")
    print("3. Add your Tavily API key to .env to test search features")

if __name__ == "__main__":
    asyncio.run(main())
