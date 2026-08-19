"""Review de mission par le Lead DevOps IA."""

import json
from dataclasses import dataclass
from typing import Any

from .llm import LLMClient
from .po import Mission
from .prompts import format_prompt


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


def review_mission(llm: LLMClient, mission: Mission, changed_files: dict[str, str]) -> Review:
    """Demande au Lead IA une review d'une mission."""
    ticket = json.dumps(mission.to_dict(), ensure_ascii=False, indent=2)
    files = json.dumps(changed_files, ensure_ascii=False, indent=2)
    prompt = format_prompt("lead", {"TICKET": ticket, "FILES": files})
    response = llm.chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un Lead DevOps Senior. "
                    "Tu fais des reviews précises et pédagogiques."
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
