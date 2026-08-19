"""Cache local des réponses LLM pour maîtriser le budget."""

import json
import time
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TTL_DAYS = 30


@dataclass
class Cache:
    """Cache de réponses LLM basé sur des fichiers JSON."""

    base_dir: Path
    ttl_days: int = DEFAULT_TTL_DAYS

    def __post_init__(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.base_dir / f"{key}.json"

    def get(self, key: str) -> str | None:
        path = self._path(key)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("expires_at", 0) < time.time():
            path.unlink()
            return None
        return str(data["content"])

    def set(self, key: str, content: str) -> None:
        path = self._path(key)
        expires_at = time.time() + self.ttl_days * 24 * 3600
        data = {"content": content, "expires_at": expires_at, "cached_at": time.time()}
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def clear(self) -> None:
        for path in self.base_dir.glob("*.json"):
            path.unlink()
