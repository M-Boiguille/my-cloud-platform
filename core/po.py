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
    lines.append("Modules en cours :")
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


def _validate_mission(data: dict[str, Any]) -> list[str]:
    """Détecte les incohérences et contradictions dans une mission générée."""
    errors: list[str] = []

    # Champs obligatoires
    required = [
        "title",
        "description",
        "acceptance_criteria",
        "level",
        "deliverables",
        "prerequisites",
        "new_concepts",
    ]
    for key in required:
        if not data.get(key):
            errors.append(f"Champ requis manquant : {key}")

    # Niveau autorisé
    valid_levels = {"debutant", "junior", "confirme", "senior"}
    level = data.get("level", "")
    if level not in valid_levels:
        errors.append(f"Niveau '{level}' non autorisé. Utilise : {valid_levels}")

    # Durée positive
    if data.get("estimated_time_minutes", 0) <= 0:
        errors.append("estimated_time_minutes doit être > 0")

    # Critères non vides
    criteria = data.get("acceptance_criteria", [])
    if not criteria:
        errors.append("acceptance_criteria ne doit pas être vide")

    # Vérifier la cohérence des critères
    all_criteria = "\n".join(criteria).lower()
    all_text = (data.get("description", "") + data.get("constraints", "")).lower()

    # Conflit port privilégié + non-root
    if "non-root" in all_text or "non root" in all_text:
        for port in ["80", "443", "22"]:
            if f"port {port}" in all_text or " -p " in all_text and f":{port}" in all_text:
                errors.append(
                    f"Conflit détecté : exécution non-root incompatible avec le port {port} "
                    "(port privilégié). Soit supprime le non-root, soit utilise un port > 1024."
                )

    # Conflit docker run port droite/gauche
    for criterion in criteria:
        if "docker run -p" in criterion:
            parts = criterion.split("docker run -p")
            for part in parts[1:]:
                mapping = part.split()[0].strip()
                if ":" in mapping:
                    host, container = mapping.split(":", 1)
                    # Si le conteneur est 80, on ne peut pas exiger non-root
                    if container == "80" and "non-root" in all_text:
                        errors.append(
                            "Conflit : docker run -p 8080:80 exige root dans le conteneur. "
                            "Ne pas exiger le non-root avec ce mapping."
                        )

    # Incohérence image non-root et nginx par défaut
    if "nginx:alpine" in all_criteria and "non-root" in all_text:
        errors.append(
            "Conflit : nginx:alpine par défaut tourne root sur le port 80. "
            "Ne pas imposer le non-root pour cette image."
        )

    # Best practices avancées exigées sans être optionnelles
    advanced_practices = [
        "non-root",
        "least-privilege",
        "cosign",
        "vault",
        "vault",
        "secrets",
        "pod security",
    ]
    if data.get("level") == "debutant":
        for practice in advanced_practices:
            if practice in all_text and "optionnel" not in all_text and "bonus" not in all_text:
                errors.append(
                    f"La best practice '{practice}' ne peut pas être exigée "
                    "en mission débutante. Précise qu'elle est optionnelle/bonus."
                )

    # Prérequis non vides et cohérents
    if not data.get("prerequisites"):
        errors.append("prerequisites ne doit pas être vide")

    # Livrables cohérents avec les critères
    if not data.get("deliverables"):
        errors.append("deliverables ne doit pas être vide")

    return errors


def _fix_prompt(mission_id: str, current: dict[str, Any], errors: list[str]) -> str:
    """Construit un prompt pour corriger une mission invalide."""
    return (
        "Tu es un architecte SRE. La mission générée ci-dessous contient "
        "des erreurs. Corrige-la sans ajouter d'explications. "
        "Conserve le format JSON exact.\n\n"
        "ERREURS À CORRIGER :\n"
        + "\n".join(f"- {err}" for err in errors)
        + "\n\nMISSION ACTUELLE :\n"
        + json.dumps(current, ensure_ascii=False, indent=2)
    )


def _generate_raw(llm: LLMClient, prompt: str) -> dict[str, Any]:
    response = llm.chat(
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un Product Owner DevOps "
                    "qui génère des missions pédagogiques cohérentes."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        json_mode=True,
    )
    cleaned = _clean_json(response)
    try:
        data: dict[str, Any] = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Réponse IA non valide : {cleaned}") from e
    if not isinstance(data, dict):
        raise ValueError(f"La réponse n'est pas un objet JSON : {cleaned}")
    return data


def generate_mission(llm: LLMClient, progress: Progress, mission_id: str) -> Mission:
    """Génère une mission adaptée au profil du joueur, avec validation et retry."""
    prompt = format_prompt(
        "po",
        {
            "PROGRESS": _format_progress(progress),
            "LEVEL": progress.player.current_level,
        },
    )
    data = _generate_raw(llm, prompt)
    data["mission_id"] = mission_id

    for _ in range(3):
        errors = _validate_mission(data)
        if not errors:
            break
        print("Mission invalide, tentative de correction :", errors)
        fix_prompt = _fix_prompt(mission_id, data, errors)
        data = _generate_raw(llm, fix_prompt)
        data["mission_id"] = mission_id
    else:
        raise ValueError(
            "Impossible de générer une mission valide après 3 tentatives : "
            + ", ".join(errors)
        )

    return Mission.from_dict(data)


def generate_custom_mission(
    llm: LLMClient, progress: Progress, mission_id: str, topic: str
) -> Mission:
    """Génère une mission sur un sujet personnalisé."""
    prompt = format_prompt(
        "po_custom",
        {
            "TOPIC": topic,
            "PROGRESS": _format_progress(progress),
            "LEVEL": progress.player.current_level,
        },
    )
    data = _generate_raw(llm, prompt)
    data["mission_id"] = mission_id

    for _ in range(3):
        errors = _validate_mission(data)
        if not errors:
            break
        print("Mission invalide, tentative de correction :", errors)
        fix_prompt = _fix_prompt(mission_id, data, errors)
        data = _generate_raw(llm, fix_prompt)
        data["mission_id"] = mission_id
    else:
        raise ValueError(
            "Impossible de générer une mission valide après 3 tentatives : "
            + ", ".join(errors)
        )

    return Mission.from_dict(data)
