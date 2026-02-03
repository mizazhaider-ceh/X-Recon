# config.py
# this file stores all our secret api keys.
# never share this file or upload it to a public github repository!

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# get your free key from https://cloud.cerebras.ai/
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

if not CEREBRAS_API_KEY:
    # Fallback to a warning or empty string, but don't crash immediately unless used
    print("Warning: CEREBRAS_API_KEY not found in .env file.")