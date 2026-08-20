#!/usr/bin/env python3
"""CLI my-cloud-platform."""

import argparse
import json
import subprocess
from pathlib import Path

from core.cache import Cache
from core.llm import load_llm_from_env
from core.po import generate_mission
from core.state import load_progress


def _list_mission_files() -> list[Path]:
    """Liste les fichiers de mission générés, triés."""
    generated_dir = Path("missions/mcp/generated")
    if not generated_dir.exists():
        return []
    return sorted(generated_dir.glob("mcp-*.json"))


def get_current_mission() -> str | None:
    """Retourne le dernier mission_id généré."""

    files = _list_mission_files()
    if not files:
        return None
    return files[-1].stem


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


def cmd_regenerate() -> None:
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
    mission = generate_mission(llm, progress, new_id)

    out_dir = Path("missions/mcp/generated")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{mission.mission_id}.json"
    out_file.write_text(
        json.dumps(mission.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Nouvelle mission générée : {out_file}")
    print(f"Titre : {mission.title}")


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

    args = parser.parse_args()

    if args.start:
        cmd_start()
    elif args.status:
        cmd_status()
    elif args.regenerate:
        cmd_regenerate()
    elif args.submit:
        cmd_submit()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
