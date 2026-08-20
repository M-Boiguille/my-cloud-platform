"""Review de mission par le Lead DevOps IA."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .llm import LLMClient
from .po import Mission
from .prompts import format_prompt


def _read_learned(changed_files: dict[str, str]) -> str:
    """Extrait le contenu de LEARNED.md s'il est présent."""
    for path, content in changed_files.items():
        if Path(path).name.lower() == "learned.md":
            return f"--- {path} ---\n{content}\n"
    # Fallback : cherche LEARNED.md sur disque
    for p in Path(".").rglob("LEARNED.md"):
        return f"--- {p} ---\n{p.read_text(encoding='utf-8')}\n"
    return "Aucun fichier LEARNED.md fourni."


@dataclass
class Review:
    decision: str
    score: int
    points_forts: list[str]
    points_a_corriger: list[str]
    explications_pedagogiques: list[str]
    next_step: str

    def is_approved(self) -> bool:
        return self.decision.upper() == "APPROUVÉ" or self.score >= 80

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "score": self.score,
            "points_forts": self.points_forts,
            "points_a_corriger": self.points_a_corriger,
            "explications_pedagogiques": self.explications_pedagogiques,
            "next_step": self.next_step,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Review":
        return cls(
            decision=data.get("decision", "À_REVOIR"),
            score=data.get("score", 0),
            points_forts=data.get("points_forts", []),
            points_a_corriger=data.get("points_a_corriger", []),
            explications_pedagogiques=data.get("explications_pedagogiques", []),
            next_step=data.get("next_step", ""),
        )


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


def review_mission(
    llm: LLMClient,
    mission: Mission,
    changed_files: dict[str, str],
    previous_reviews: str = "",
) -> Review:
    """Demande au Lead IA une review d'une mission."""
    ticket = json.dumps(mission.to_dict(), ensure_ascii=False, indent=2)
    files = json.dumps(changed_files, ensure_ascii=False, indent=2)
    learned = _read_learned(changed_files)
    prompt = format_prompt(
        "lead",
        {
            "TICKET": ticket,
            "PREVIOUS_REVIEWS": previous_reviews or "Aucune review précédente.",
            "LEARNED": learned,
            "FILES": files,
        },
    )
    response = llm.chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un Lead DevOps Senior. "
                    "Tu fais des reviews précises, cohérentes et pédagogiques."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        json_mode=True,
    )
    cleaned = _clean_json(response)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Réponse Lead IA non valide : {cleaned}") from e

    return Review.from_dict(data)
