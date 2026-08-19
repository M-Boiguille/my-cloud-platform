"""Génération du dashboard statique."""

import json
from pathlib import Path
from typing import Any

from .state import load_progress

METRICS_FILE = Path("web/metrics.json")


SKILL_LABELS = {
    "Linux_Reseau": "Linux / Réseau",
    "Docker": "Docker",
    "Kubernetes": "Kubernetes",
    "CI_CD": "CI/CD",
    "Terraform": "Terraform",
    "Observabilite_Securite": "Observabilité",
    "Ansible": "Ansible",
}


def generate_metrics() -> dict[str, Any]:
    """Génère le fichier metrics.json pour le dashboard."""
    progress = load_progress()

    skills = {SKILL_LABELS.get(k, k): v for k, v in progress.skills.items()}

    return {
        "player": progress.player.name,
        "level": progress.player.current_level,
        "target_level": getattr(progress.player, "target_level", ""),
        "missions_completed": len(progress.completed_missions),
        "skills": skills,
        "known_concepts_count": len(progress.known_concepts),
        "upcoming_concepts_count": len(progress.upcoming_concepts),
        "active_courses": [c["name"] for c in progress.player.active_courses],
    }


def update_dashboard() -> Path:
    """Écrit le fichier metrics.json."""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    metrics = generate_metrics()
    METRICS_FILE.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    return METRICS_FILE
