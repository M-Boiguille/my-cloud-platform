"""Génère le fichier missions.json pour la page de suivi."""

import json
from pathlib import Path
from typing import Any

MISSIONS_DIR = Path("missions/mcp/generated")
OUTPUT = Path("web/missions.json")


def build_missions_index() -> list[dict[str, Any]]:
    """Construit l'index JSON de toutes les missions."""
    missions: list[dict[str, Any]] = []
    if not MISSIONS_DIR.exists():
        return missions

    for file in sorted(MISSIONS_DIR.glob("mcp-*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))
        missions.append(
            {
                "mission_id": data.get("mission_id", file.stem),
                "title": data.get("title", ""),
                "level": data.get("level", ""),
                "deadline": data.get("deadline", ""),
                "estimated_time_minutes": data.get("estimated_time_minutes", 0),
                "data": data,
            }
        )

    if missions:
        # La mission en cours = la dernière de la liste triée
        for m in missions:
            m["current"] = False
        missions[-1]["current"] = True

    return missions


def update_missions_json() -> Path:
    """Écrit le fichier web/missions.json."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    index = build_missions_index()
    OUTPUT.write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return OUTPUT


if __name__ == "__main__":
    update_missions_json()
