#!/usr/bin/env python3
"""Génère une nouvelle mission pour my-cloud-platform."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.cache import Cache
from core.llm import load_llm_from_env
from core.po import generate_mission
from core.state import load_career, load_progress

MISSIONS_DIR = Path("missions/mcp/generated")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def _max_mission_number():
    """Récupère le plus grand numéro de mission déjà généré localement."""
    if not MISSIONS_DIR.exists():
        return 0
    numbers = []
    for file in MISSIONS_DIR.glob("mcp-*.json"):
        try:
            num = int(file.stem.split("-")[1])
            numbers.append(num)
        except ValueError:
            continue
    return max(numbers, default=0)


def _max_issue_number():
    """Récupère le plus grand numéro de mission déjà utilisé dans les issues."""
    if not REPO or not GITHUB_TOKEN:
        return 0
    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    params = {"labels": "mission", "state": "all", "per_page": 100}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return 0
    numbers = []
    pattern = re.compile(r"\[Mission mcp-(\d{3})\]")
    for issue in response.json():
        title = issue.get("title", "")
        match = pattern.search(title)
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0)


def _mission_numbers(items):
    """Extrait les numéros de mission d'une liste d'IDs."""
    numbers = []
    pattern = re.compile(r"mcp-(\d{3})")
    for item in items:
        match = pattern.search(str(item))
        if match:
            numbers.append(int(match.group(1)))
    return numbers


def find_next_mission_id(progress, career):
    """Détermine le prochain identifiant de mission sans saut."""
    completed_numbers = _mission_numbers(
        career.get("missions_completed", []) + progress.completed_missions
    )
    local_max = _max_mission_number()
    issue_max = _max_issue_number()
    next_num = max(completed_numbers + [local_max, issue_max], default=0) + 1
    return f"mcp-{next_num:03d}"


def create_issue(mission):
    """Crée une issue GitHub pour la mission."""
    if not REPO or not GITHUB_TOKEN:
        print("GITHUB_REPOSITORY ou GITHUB_TOKEN manquant. Issue non créée.")
        return None

    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    body = f"""## Mission automatique générée par IA

|**Mission :** {mission.mission_id}
|**Niveau :** {mission.level}
|**Temps estimé :** {mission.estimated_time_minutes} minutes
|**Deadline :** {mission.deadline}

### Brief

{mission.client_brief}

### Contexte

{mission.description}

### Impact

{mission.business_impact}

### Contraintes

{mission.constraints}

### Nouvelles notions

"""
    for concept in mission.new_concepts:
        body += f"- {concept}\n"

    body += "\n### Prérequis\n\n"
    for prereq in mission.prerequisites:
        body += f"- {prereq}\n"

    body += "\n### Liens d'apprentissage\n\n"
    for link in mission.learning_links:
        body += f"- {link}\n"

    body += "\n### Critères d'acceptation\n\n"
    for criterion in mission.acceptance_criteria:
        body += f"- [ ] {criterion}\n"

    if mission.deliverables:
        body += "\n### Livrables\n\n"
        for item in mission.deliverables:
            body += f"- {item}\n"

    data = {
        "title": f"[Mission {mission.mission_id}] {mission.title}",
        "body": body,
        "labels": ["mission", "generated-by-ai"],
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def save_mission(mission):
    """Sauvegarde la mission générée sur disque."""
    MISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    mission_file = MISSIONS_DIR / f"{mission.mission_id}.json"
    mission_file.write_text(
        json.dumps(mission.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Mission sauvegardée : {mission_file}")
    return mission_file


def git_commit_and_push(file_path, message):
    """Commit et pousse le fichier de mission sur main."""
    subprocess.run(["git", "add", str(file_path)], check=True)
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            "github-actions[bot]@users.noreply.github.com",
        ],
        check=True,
    )
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


def main():
    cache = Cache(Path("data/cache/llm"))
    llm = load_llm_from_env(cache)
    progress = load_progress()
    career = load_career()

    mission_id = find_next_mission_id(progress, career)
    mission = generate_mission(llm, progress, mission_id)

    mission_file = save_mission(mission)
    git_commit_and_push(
        mission_file,
        f"chore: generate mission {mission.mission_id}",
    )
    issue = create_issue(mission)
    if issue:
        print(f"Issue créée : {issue['html_url']}")


if __name__ == "__main__":
    main()
