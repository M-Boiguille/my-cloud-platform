"""Évaluation pédagogique d'une mission par le mentor IA."""

import json
from dataclasses import dataclass
from typing import Any

from .courses import load_courses
from .llm import LLMClient
from .prompts import format_prompt


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


@dataclass
class Evaluation:
    date: str
    mission: str
    score: int
    concepts_valides: list[str]
    concepts_a_revoir: list[str]
    skills_updates: dict[str, int]
    key_lesson: str
    recommendation: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Evaluation":
        return cls(
            date=data.get("date", ""),
            mission=data.get("mission", ""),
            score=data.get("score", 0),
            concepts_valides=data.get("concepts_valides", []),
            concepts_a_revoir=data.get("concepts_a_revoir", []),
            skills_updates=data.get("skills_updates", {}),
            key_lesson=data.get("key_lesson", ""),
            recommendation=data.get("recommendation", ""),
        )


def _format_courses() -> str:
    courses = load_courses()
    lines = []
    for course in courses:
        for module in course.modules:
            concepts = ", ".join(module.concepts)
            status = "✅" if module.completed else "⬜"
            lines.append(f"- {status} [{course.name}] {module.name}: {concepts}")
    return "\n".join(lines)


def evaluate_mission(
    llm: LLMClient,
    mission_data: dict[str, Any],
    files: dict[str, str],
    review: dict[str, Any],
) -> Evaluation:
    """Génère une évaluation pédagogique après mission."""
    progress = f"Score Lead : {review.get('score', 0)}\n"
    progress += "Points forts :\n" + "\n".join(f"- {p}" for p in review.get("points_forts", []))
    progress += "\nPoints à corriger :\n" + "\n".join(
        f"- {p}" for p in review.get("points_a_corriger", [])
    )

    files_str = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in files.items()
    )

    prompt = format_prompt(
        "evaluator",
        {
            "MISSION": json.dumps(mission_data, ensure_ascii=False, indent=2),
            "FILES": files_str[:4000],  # limiter la taille
            "REVIEW": json.dumps(review, ensure_ascii=False, indent=2),
            "COURSES": _format_courses(),
        },
    )

    response = llm.chat(
        messages=[
            {
                "role": "system",
                "content": "Tu es un mentor DevOps qui évalue et ajuste le plan de formation.",
            },
            {"role": "user", "content": prompt},
        ],
        json_mode=True,
    )
    cleaned = _clean_json(response)
    data = json.loads(cleaned)
    return Evaluation.from_dict(data)
