# tools/env_bootstrap.py
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load .env from CWD if present (when you launch from repo root)
load_dotenv(Path.cwd() / ".env", override=False)

# Also try standard discovery (walks up directories)
load_dotenv(find_dotenv(), override=True)  # override=True avoids empty system vars shadowing
