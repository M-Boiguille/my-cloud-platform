"""Génération de missions par le Product Owner IA."""

import json
from dataclasses import dataclass
from typing import Any

from .llm import LLMClient
from .prompts import format_prompt
from .state import Progress


@dataclass
class Mission:
    mission_id: str
    title: str
    level: str
    client_brief: str
    description: str
    business_impact: str
    constraints: str
    deadline: str
    new_concepts: list[str]
    prerequisites: list[str]
    learning_links: list[str]
    acceptance_criteria: list[str]
    estimated_time_minutes: int
    deliverables: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "title": self.title,
            "level": self.level,
            "client_brief": self.client_brief,
            "description": self.description,
            "business_impact": self.business_impact,
            "constraints": self.constraints,
            "deadline": self.deadline,
            "new_concepts": self.new_concepts,
            "prerequisites": self.prerequisites,
            "learning_links": self.learning_links,
            "acceptance_criteria": self.acceptance_criteria,
            "estimated_time_minutes": self.estimated_time_minutes,
            "deliverables": self.deliverables,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Mission":
        return cls(
            mission_id=data["mission_id"],
            title=data["title"],
            level=data["level"],
            client_brief=data.get("client_brief", ""),
            description=data["description"],
            business_impact=data.get("business_impact", ""),
            constraints=data.get("constraints", ""),
            deadline=data.get("deadline", ""),
            new_concepts=data.get("new_concepts", []),
            prerequisites=data.get("prerequisites", []),
            learning_links=data.get("learning_links", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            estimated_time_minutes=data.get("estimated_time_minutes", 120),
            deliverables=data.get("deliverables", []),
        )


def _format_progress(progress: Progress) -> str:
    lines = [f"Niveau actuel : {progress.player.current_level}"]
    lines.append("Compétences :")
    for skill, value in sorted(progress.skills.items()):
        lines.append(f"- {skill}: {value}/100")
    lines.append("Concepts connus :")
    for concept in progress.known_concepts:
        lines.append(f"- {concept}")
    lines.append("Prochaines notions à découvrir :")
    for concept in progress.upcoming_concepts:
        lines.append(f"- {concept}")
    lines.append("Modules KodeKloud en cours :")
    for course in progress.player.active_courses:
        in_progress = ", ".join(course.get("modules_in_progress", []))
        lines.append(
            f"- {course['name']} : {course.get('progress', '?')} "
            f"— module en cours: {in_progress}",
        )
    return "\n".join(lines)


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


def generate_mission(llm: LLMClient, progress: Progress, mission_id: str) -> Mission:
    """Génère une mission adaptée au profil du joueur."""
    prompt = format_prompt(
        "po",
        {
            "PROGRESS": _format_progress(progress),
            "LEVEL": progress.player.current_level,
        },
    )
    response = llm.chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un Product Owner DevOps "
                    "qui génère des missions pédagogiques."
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
        raise ValueError(f"Réponse IA non valide : {cleaned}") from e

    data["mission_id"] = mission_id
    # Validation minimale
    required = ["title", "description", "acceptance_criteria", "level"]
    for key in required:
        if not data.get(key):
            raise ValueError(f"Mission invalide : champ '{key}' manquant")
    return Mission.from_dict(data)
