"""Gestion des cours et calcul des concepts connus/à venir."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

COURSES_FILE = Path("data/courses.yml")


@dataclass
class Module:
    name: str
    concepts: list[str] = field(default_factory=list)
    completed: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Module":
        return cls(
            name=data["name"],
            concepts=data.get("concepts", []),
            completed=data.get("completed", False),
        )


@dataclass
class Course:
    name: str
    url: str
    modules: list[Module] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Course":
        return cls(
            name=data["name"],
            url=data.get("url", ""),
            modules=[Module.from_dict(m) for m in data.get("modules", [])],
        )


def load_courses() -> list[Course]:
    if not COURSES_FILE.exists():
        return []
    data = yaml.safe_load(COURSES_FILE.read_text(encoding="utf-8"))
    return [Course.from_dict(c) for c in data.get("courses", [])]


def compute_concepts(
    courses: list[Course] | None = None,
    validated_concepts: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Renvoie (known_concepts, upcoming_concepts) calculés depuis les modules complétés.

    Les `validated_concepts` sont ajoutés aux concepts connus.
    """
    if courses is None:
        courses = load_courses()
    if validated_concepts is None:
        validated_concepts = set()
    known: set[str] = set(validated_concepts)
    upcoming: set[str] = set()
    for course in courses:
        for module in course.modules:
            if module.completed:
                known.update(module.concepts)
            else:
                upcoming.update(module.concepts)
    upcoming -= known
    return sorted(known), sorted(upcoming)


def compute_skills(courses: list[Course] | None = None) -> dict[str, int]:
    """Calcule un score par domaine en fonction des modules complétés.

    Scores approximatifs :
    - Linux / Reseau : Shell, Git, Bash
    - Docker : non couvert ici, à garder depuis progress.yml
    - Kubernetes : CKA, Kubernetes Networking
    - CI_CD : GitHub Actions, Git
    - Terraform : Terraform
    - Observabilite_Securite : Prometheus, Loki
    - Ansible : Ansible
    """
    if courses is None:
        courses = load_courses()

    totals = {
        "Linux_Reseau": 0,
        "Docker": 0,
        "Kubernetes": 0,
        "CI_CD": 0,
        "Terraform": 0,
        "Observabilite_Securite": 0,
        "Ansible": 0,
    }
    completed = {
        "Linux_Reseau": 0,
        "Docker": 0,
        "Kubernetes": 0,
        "CI_CD": 0,
        "Terraform": 0,
        "Observabilite_Securite": 0,
        "Ansible": 0,
    }

    mapping = {
        "CKA": "Kubernetes",
        "Kubernetes Networking": "Kubernetes",
        "Git": "CI_CD",
        "Shell Scripts for Beginners": "Linux_Reseau",
        "Advanced Bash Scripting": "Linux_Reseau",
        "Terraform Associate Certification": "Terraform",
        "GitHub Actions": "CI_CD",
        "Ansible Basics": "Ansible",
        "Prometheus Certified Associate": "Observabilite_Securite",
        "Grafana Loki": "Observabilite_Securite",
    }

    for course in courses:
        bucket = mapping.get(course.name)
        if not bucket:
            continue
        for module in course.modules:
            totals[bucket] += 1
            if module.completed:
                completed[bucket] += 1

    skills = {}
    for bucket in totals:
        if totals[bucket] == 0:
            skills[bucket] = 0
        else:
            skills[bucket] = int((completed[bucket] / totals[bucket]) * 100)
    return skills


def get_active_courses(courses: list[Course] | None = None) -> list[dict[str, Any]]:
    """Renvoie les cours avec au moins un module complété mais pas terminé."""
    if courses is None:
        courses = load_courses()
    active = []
    for course in courses:
        completed = [m for m in course.modules if m.completed]
        if completed and not all(m.completed for m in course.modules):
            active.append(
                {
                    "name": course.name,
                    "url": course.url,
                    "completed_modules": len(completed),
                    "total_modules": len(course.modules),
                }
            )
    return active
