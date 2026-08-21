#!/usr/bin/env python3
"""CLI my-cloud-platform."""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

import requests

from core.cache import Cache
from core.llm import load_llm_from_env
from core.po import generate_custom_mission, generate_mission
from core.state import load_progress

MISSIONS_DIR = Path("missions/mcp/generated")
REPO = os.environ.get("GITHUB_REPOSITORY", "")


def _list_mission_files() -> list[Path]:
    """Liste les fichiers de mission générés, triés."""
    if not MISSIONS_DIR.exists():
        return []
    return sorted(MISSIONS_DIR.glob("mcp-*.json"))


def _mission_numbers(items):
    """Extrait les numéros de mission d'une liste d'IDs."""
    numbers = []
    pattern = re.compile(r"mcp-(\d{3})")
    for item in items:
        match = pattern.search(str(item))
        if match:
            numbers.append(int(match.group(1)))
    return numbers


def _find_next_mission_id() -> str:
    """Détermine le prochain identifiant de mission sans saut."""
    files = _list_mission_files()
    numbers = _mission_numbers([f.stem for f in files])
    next_num = max(numbers, default=0) + 1
    return f"mcp-{next_num:03d}"


def get_current_mission() -> str | None:
    """Retourne le dernier mission_id généré."""
    files = _list_mission_files()
    if not files:
        return None
    return files[-1].stem


def _save_mission(mission) -> Path:
    """Sauvegarde la mission générée sur disque."""
    MISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    mission_file = MISSIONS_DIR / f"{mission.mission_id}.json"
    mission_file.write_text(
        json.dumps(mission.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return mission_file


def _create_issue(mission) -> str | None:
    """Crée une issue GitHub pour la mission."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not REPO or not token:
        print("GITHUB_REPOSITORY ou GITHUB_TOKEN manquant. Issue non créée.")
        return None

    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    body = f"""## Mission générée

|**Mission :** {mission.mission_id}
|**Niveau :** {mission.level}
|**Temps estimé :** {mission.estimated_time_minutes} minutes
|**Deadline :** {mission.deadline}

### Contexte

{mission.description}

### Critères d'acceptation

"""
    for criterion in mission.acceptance_criteria:
        body += f"- [ ] {criterion}\n"

    data = {
        "title": f"[Mission {mission.mission_id}] {mission.title}",
        "body": body,
        "labels": ["mission"],
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json().get("html_url")
    print(f"Erreur création issue : {response.status_code} {response.text}")
    return None


def cmd_start() -> None:
    """Affiche la mission en cours."""
    mission_id = get_current_mission()
    if not mission_id:
        print("Aucune mission en cours. Lance d'abord le workflow 'Generate next mission'.")
        return

    mission_file = Path(f"missions/mcp/generated/{mission_id}.json")
    mission = json.loads(mission_file.read_text(encoding="utf-8"))

    print(f"\nMission en cours : {mission_id}")
    print(f"Titre : {mission['title']}")
    print(f"Niveau : {mission['level']}")
    print(f"Temps estimé : {mission.get('estimated_time_minutes', '?')} min")
    print(f"\nDescription :\n{mission['description']}\n")
    print("Nouvelles notions :")
    for concept in mission.get("new_concepts", []):
        print(f"  - {concept}")
    print("\nPrérequis :")
    for prereq in mission.get("prerequisites", []):
        print(f"  - {prereq}")
    print("\nCritères d'acceptation :")
    for i, criterion in enumerate(mission.get("acceptance_criteria", []), 1):
        print(f"  {i}. {criterion}")


def cmd_status() -> None:
    """Affiche le niveau et l'historique."""
    progress = load_progress()
    print(f"\nProfil : {progress.player.name}")
    print(f"Niveau : {progress.player.current_level}")
    print(f"Cible : {progress.player.target_level}")
    print(f"Missions validées : {len(progress.completed_missions)}")
    print("\nCompétences :")
    for skill, value in sorted(progress.skills.items()):
        print(f"  {skill}: {value}/100")


def cmd_regenerate(level: str | None = None) -> None:
    """Redemande une nouvelle génération de mission."""
    progress = load_progress()
    mission_id = get_current_mission()
    if mission_id:
        mission_file = Path(f"missions/mcp/generated/{mission_id}.json")
        if mission_file.exists():
            mission_file.unlink()
            print(f"Mission {mission_id} supprimée. On en génère une nouvelle...")

    cache = Cache(Path("data/cache/llm"))
    llm = load_llm_from_env(cache)
    new_id = f"{mission_id or 'mcp-001'}-regen"
    mission = generate_mission(llm, progress, new_id, level=level)
    out_file = _save_mission(mission)
    print(f"Nouvelle mission générée : {out_file}")
    print(f"Titre : {mission.title}")
    print(f"Niveau : {mission.level}")


def cmd_custom(topic: str, level: str | None = None) -> None:
    """Génère une mission personnalisée sur un sujet donné."""
    progress = load_progress()
    mission_id = _find_next_mission_id()

    cache = Cache(Path("data/cache/llm"))
    llm = load_llm_from_env(cache)
    mission = generate_custom_mission(llm, progress, mission_id, topic, level=level)
    out_file = _save_mission(mission)

    print(f"Mission custom générée : {out_file}")
    print(f"Titre : {mission.title}")
    print(f"Niveau : {mission.level}")

    issue_url = _create_issue(mission)
    if issue_url:
        print(f"Issue créée : {issue_url}")
    else:
        print("Issue non créée. Crée-la manuellement avec :")
        print(
            f"  gh issue create --title \"[Mission {mission.mission_id}] "
            f"{mission.title}\" --body \"...\""
        )


def cmd_submit() -> None:
    """Crée une branche et ouvre une PR pour la mission en cours."""
    mission_id = get_current_mission()
    if not mission_id:
        print("Aucune mission en cours. Lance d'abord 'career.py --start'.")
        return

    branch = f"mission/{mission_id}"
    try:
        subprocess.run(["git", "checkout", "-b", branch], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"mission({mission_id}): solution"], check=True)
        subprocess.run(["git", "push", "-u", "origin", branch], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur Git : {e}")
        return

    print(f"\nBranche {branch} poussée.")
    print("Ouvre une PR manuellement, ou utilise gh :")
    print("  gh pr create ")
    print(f"    --title \"[Mission {mission_id}] solution\"")
    print(f"    --body \"Mission {mission_id}\"")


def main() -> None:
    parser = argparse.ArgumentParser(description="my-cloud-platform")
    parser.add_argument(
        "--start",
        action="store_true",
        help="Affiche la mission en cours",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Affiche le niveau et l'historique",
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Redemande une nouvelle mission",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Crée la branche et la PR pour la mission en cours",
    )
    parser.add_argument(
        "--custom-mission",
        metavar="TOPIC",
        help="Génère une mission personnalisée sur le sujet donné",
    )
    parser.add_argument(
        "--level",
        metavar="NIVEAU",
        choices=["debutant", "junior", "confirme", "senior"],
        help="Force le niveau de la mission (débutant, junior, confirme, senior)",
    )

    args = parser.parse_args()

    if args.start:
        cmd_start()
    elif args.status:
        cmd_status()
    elif args.regenerate:
        cmd_regenerate(level=args.level)
    elif args.submit:
        cmd_submit()
    elif args.custom_mission:
        cmd_custom(args.custom_mission, level=args.level)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
