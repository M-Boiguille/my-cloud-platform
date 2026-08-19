#!/usr/bin/env python3
"""Évalue une mission et met à jour la progression du joueur."""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.cache import Cache
from core.evaluator import evaluate_mission
from core.llm import load_llm_from_env
from core.state import load_progress, save_progress

REPO = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
PR_NUMBER = os.environ.get("PR_NUMBER", "")


def get_pr_info():
    if not REPO or not GITHUB_TOKEN or not PR_NUMBER:
        raise ValueError("GITHUB_REPOSITORY, GITHUB_TOKEN ou PR_NUMBER manquant")
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_pr_files():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = {}
    for f in response.json():
        patch = f.get("patch", "")
        if len(patch) > 4000:
            patch = patch[:4000] + "\n... (tronqué)"
        files[f["filename"]] = patch
    return files


def get_last_review():
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    for comment in reversed(response.json()):
        body = comment.get("body", "")
        if "## Review du Lead DevOps" in body:
            return body
    return ""


def parse_review(review_body: str) -> dict[str, Any]:
    review: dict[str, Any] = {
        "decision": "À_REVOIR",
        "score": 0,
        "points_forts": [],
        "points_a_corriger": [],
    }
    score_match = re.search(r"\*\*Score\s*:\*\*\s*(\d+)", review_body)
    if score_match:
        review["score"] = int(score_match.group(1))
    decision_match = re.search(r"\*\*Décision\s*:\*\*\s*(APPROUVÉ|À_REVOIR)", review_body)
    if decision_match:
        review["decision"] = decision_match.group(1)
    return review


def extract_mission_id(title):
    match = re.search(r"\[Mission (mcp-\d{3})\]", title)
    if not match:
        raise ValueError(f"Titre de PR invalide : {title}")
    return match.group(1)


def find_mission_file(mission_id):
    path = Path("missions/mcp/generated") / f"{mission_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Mission non trouvée : {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def update_progress(evaluation, mission_id):
    progress = load_progress()
    progress.completed_missions.append(mission_id)
    progress.completed_missions = sorted(set(progress.completed_missions))

    for concept in evaluation.concepts_valides:
        if concept not in progress.validated_concepts:
            progress.validated_concepts.append(concept)
    progress.validated_concepts = sorted(progress.validated_concepts)

    for skill, value in evaluation.skills_updates.items():
        progress.skills_overrides[skill] = max(
            0,
            min(100, value),
        )

    save_progress(progress)
    return progress


def main():
    pr = get_pr_info()
    mission_id = extract_mission_id(pr["title"])
    mission_data = find_mission_file(mission_id)
    files = get_pr_files()
    review_body = get_last_review()
    review = parse_review(review_body)

    cache = Cache(Path("data/cache/llm"))
    llm = load_llm_from_env(cache)

    evaluation = evaluate_mission(llm, mission_data, files, review)
    print(f"Évaluation : score {evaluation.score}")
    print(f"Concepts validés : {len(evaluation.concepts_valides)}")

    progress = update_progress(evaluation, mission_id)
    print(f"Progression mise à jour : {len(progress.validated_concepts)} concepts validés")

    eval_file = Path("data/state") / f"eval-{mission_id}.json"
    eval_file.parent.mkdir(parents=True, exist_ok=True)
    eval_file.write_text(
        json.dumps(
            {
                "date": evaluation.date,
                "mission": evaluation.mission,
                "score": evaluation.score,
                "concepts_valides": evaluation.concepts_valides,
                "concepts_a_revoir": evaluation.concepts_a_revoir,
                "skills_updates": evaluation.skills_updates,
                "key_lesson": evaluation.key_lesson,
                "recommendation": evaluation.recommendation,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Évaluation sauvegardée : {eval_file}")


if __name__ == "__main__":
    main()
