"""Gestion du state joueur en YAML."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .courses import compute_concepts, compute_skills, get_active_courses

PROGRESS_FILE = Path("data/progress.yml")
CAREER_FILE = Path("data/state/career.yml")
REJECTED_FILE = Path("data/state/rejected.yml")


@dataclass
class Player:
    name: str
    current_level: str
    current_mission: str | None
    target_level: str = ""
    certifications: list[dict[str, Any]] = field(default_factory=list)
    active_courses: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Progress:
    player: Player
    completed_missions: list[str]
    validated_concepts: list[str]
    skills_overrides: dict[str, int]
    skills: dict[str, int] = field(default_factory=dict)
    known_concepts: list[str] = field(default_factory=list)
    upcoming_concepts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "player": {
                "name": self.player.name,
                "current_level": self.player.current_level,
                "current_mission": self.player.current_mission,
                "target_level": self.player.target_level,
                "certifications": self.player.certifications,
                "active_courses": self.player.active_courses,
            },
            "completed_missions": self.completed_missions,
            "validated_concepts": self.validated_concepts,
            "skills_overrides": self.skills_overrides,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Progress":
        player_data = data.get("player", {})
        player = Player(
            name=player_data.get("name", "autodidact"),
            current_level=player_data.get("current_level", "confirme"),
            current_mission=player_data.get("current_mission"),
            target_level=player_data.get("target_level", ""),
            certifications=player_data.get("certifications", []),
            active_courses=player_data.get("active_courses", []),
        )
        return cls(
            player=player,
            completed_missions=data.get("completed_missions", []),
            validated_concepts=data.get("validated_concepts", []),
            skills_overrides=data.get("skills_overrides", {}),
            skills=data.get("skills", {}),
            known_concepts=data.get("known_concepts", []),
            upcoming_concepts=data.get("upcoming_concepts", []),
        )


def load_progress(path: Path = PROGRESS_FILE) -> Progress:
    """Charge le fichier de progression du joueur."""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    validated = set(data.get("validated_concepts", []))
    known, upcoming = compute_concepts(validated_concepts=validated)
    base_skills = compute_skills()
    overrides = data.get("skills_overrides", {})
    skills = {**base_skills, **overrides}
    active_courses = get_active_courses()

    data["skills"] = skills
    data["known_concepts"] = known
    data["upcoming_concepts"] = upcoming
    data.setdefault("player", {})
    data["player"]["active_courses"] = active_courses

    return Progress.from_dict(data)


def save_progress(progress: Progress, path: Path = PROGRESS_FILE) -> None:
    """Sauvegarde le fichier de progression."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(progress.to_dict(), f, sort_keys=False, allow_unicode=True)


def load_career(path: Path = CAREER_FILE) -> dict[str, Any]:
    """Charge l'historique de carrière."""
    if not path.exists():
        return {
            "level": "junior",
            "xp": 0,
            "missions_completed": [],
            "missions_rejected": [],
        }
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_career(state: dict[str, Any], path: Path = CAREER_FILE) -> None:
    """Sauvegarde l'historique de carrière."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(state, f, sort_keys=False, allow_unicode=True)


def load_last_eval() -> dict[str, Any]:
    """Charge la dernière évaluation de mission."""
    state_dir = Path("data/state")
    files = sorted(state_dir.glob("eval-mcp-*.json"))
    if not files:
        return {}
    data: dict[str, Any] = json.loads(files[-1].read_text(encoding="utf-8"))
    return data
