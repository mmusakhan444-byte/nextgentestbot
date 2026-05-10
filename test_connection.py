import os
import sys

# Try to import config
try:
    from config import AI_AGENT_PATH
    print("✅ Config file loaded successfully")
except Exception as e:
    print(f"❌ Error loading config: {e}")
    AI_AGENT_PATH = r"C:\Users\Administrator\Desktop\ai-test-agent"
    print(f"Using default path: {AI_AGENT_PATH}")

print("\n" + "="*50)
print("🔍 TESTING CONNECTION TO AI TEST AGENT")
print("="*50)

# Check if agent folder exists
print(f"\n📁 Agent path: {AI_AGENT_PATH}")
if os.path.exists(AI_AGENT_PATH):
    print("✅✅✅ AGENT FOLDER FOUND! ✅✅✅")
    
    # List contents of agent folder
    print("\n📋 Contents of agent folder:")
    items = os.listdir(AI_AGENT_PATH)
    for item in items[:10]:  # Show first 10 items
        item_path = os.path.join(AI_AGENT_PATH, item)
        if os.path.isdir(item_path):
            print(f"  📁 {item}/")
        else:
            size = os.path.getsize(item_path)
            print(f"  📄 {item} ({size} bytes)")
    
    # Check for key files
    print("\n🔍 Checking for required files:")
    
    required_files = [
        "run_with_plan.py",
        "tests/test_ai_generated.py",
        "reports/"
    ]
    
    for req in required_files:
        full_path = os.path.join(AI_AGENT_PATH, req)
        if os.path.exists(full_path):
            print(f"  ✅ Found: {req}")
        else:
            print(f"  ❌ Missing: {req}")
    
    # Check if we can list reports
    reports_dir = os.path.join(AI_AGENT_PATH, "reports")
    if os.path.exists(reports_dir):
        reports = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
        print(f"\n📊 Found {len(reports)} HTML reports in reports folder")
        if reports:
            print("  Latest reports:")
            for report in sorted(reports, reverse=True)[:3]:
                print(f"    📄 {report}")
    
else:
    print("❌❌❌ AGENT FOLDER NOT FOUND! ❌❌❌")
    print("\n🔧 FIX THIS BY:")
    print("1. Check if the folder exists at: C:\\Users\\Administrator\\Desktop\\ai-test-agent")
    print("2. Update config.py with the correct path")
    print("3. Run this test again")

print("\n" + "="*50)
print("🏁 TEST COMPLETE")
print("="*50)

# Try to import test_runner
print("\n🔧 Testing if we can import test_runner...")
try:
    from utils.test_runner import get_test_list
    print("✅ Successfully imported test_runner")
    
    # Test getting test lists
    print("\n📋 Test lists by plan:")
    for plan in ["basic", "plus", "premium"]:
        tests = get_test_list(plan)
        print(f"  {plan.upper()}: {len(tests)} tests")
        if len(tests) > 0:
            print(f"    First test: {tests[0]}")
    
except Exception as e:
    print(f"❌ Error importing test_runner: {e}")

input("\nPress Enter to exit...")