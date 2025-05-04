import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Eleven Labs API configuration
ELEVEN_LABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVEN_LABS_API_URL = "https://api.elevenlabs.io/v1"

# Audio processing settings
MAX_SEGMENT_DURATION_MS = 1 * 60 * 1000  # 4 minutes in milliseconds
MAX_API_DURATION_MS = 5 * 60 * 1000      # 5 minutes in milliseconds

# Default voice pricing
DEFAULT_VOICE_PRICE_PER_MIN = 0.20
