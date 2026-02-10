import json
from pathlib import Path
from typing import Any, Dict

from app.schemas.polling import PollingSettings

STATE_PATH = Path(__file__).resolve().parent / "polling_state.json"


def load_polling_state() -> Dict[str, Any]:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return PollingSettings().model_dump()


def save_polling_state(data: Dict[str, Any]) -> Dict[str, Any]:
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data
