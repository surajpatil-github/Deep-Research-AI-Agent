# tools/env_bootstrap.py
from pathlib import Path
from dotenv import load_dotenv, find_dotenv


load_dotenv(Path.cwd() / ".env", override=False)


load_dotenv(find_dotenv(), override=True)  
