import os

# Path to your real AI test agent
AI_AGENT_PATH = r"C:\Users\Administrator\Desktop\ai-test-agent"

# API Configuration (for future expansion)
API_HOST = "localhost"
API_PORT = 5000

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")

# Test configuration
DEFAULT_TIMEOUT = 300  # 5 minutes
HEADLESS_MODE = True