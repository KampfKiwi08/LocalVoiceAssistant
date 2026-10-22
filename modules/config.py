import json
from pathlib import Path

config_path = Path(__file__).resolve().parent.parent / "config.json"

cfg = json.loads(config_path.read_text(encoding="utf-8"))
