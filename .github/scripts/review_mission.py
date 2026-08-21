#!/usr/bin/env python3
"""Review automatique d'une mission par le Lead IA."""

import json
import os
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.cache import Cache
from core.lead import review_mission
from core.llm import load_llm_from_env
from core.po import Mission

REPO = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
PR_NUMBER = os.environ.get("PR_NUMBER", "")


def _priority_key(filename):
    """Priorise les fichiers les plus importants pour la review."""
    priorities = {
        "LEARNED.md": 0,
        "Dockerfile": 1,
        "runbook.md": 2,
        "index.html": 3,
    }
    return priorities.get(Path(filename).name, 100)


def get_pr_files(pr_number):
    """Récupère les fichiers modifiés d'une PR via l'API GitHub."""
    if not REPO or not GITHUB_TOKEN:
        print("GITHUB_REPOSITORY ou GITHUB_TOKEN manquant.")
        return {}

    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    files = response.json()

    result = {}
    for file in files:
        if file.get("patch") and len(file["patch"]) < 50_000:
            result[file["filename"]] = file["patch"]

    # Trier par priorité pour placer les fichiers importants en début de contexte
    return dict(sorted(result.items(), key=lambda x: _priority_key(x[0])))


def get_pr_body(pr_number):
    """Récupère le body de la PR pour extraire le mission_id."""
    if not REPO or not GITHUB_TOKEN:
        return ""

    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("body", "")


def get_previous_reviews(pr_number):
    """Récupère les reviews Lead précédentes sur la PR."""
    if not REPO or not GITHUB_TOKEN:
        return ""

    url = f"https://api.github.com/repos/{REPO}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    reviews = []
    for comment in response.json():
        body = comment.get("body", "")
        if "## Review du Lead DevOps" in body:
            reviews.append(body)
    if not reviews:
        return ""
    return "\n\n---\n\n".join(reviews[-3:])


def extract_mission_id(body):
    """Extrait le mission_id du body de la PR."""
    match = re.search(r"Mission (mcp-\d{3})", body)
    if match:
        return match.group(1)
    return None


def post_review(pr_number, review, score):
    """Poste le commentaire de review sur la PR."""
    if not REPO or not GITHUB_TOKEN:
        print("GITHUB_REPOSITORY ou GITHUB_TOKEN manquant.")
        return None

    url = f"https://api.github.com/repos/{REPO}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    body = "## Review du Lead DevOps\n\n"
    body += f"**Décision :** {review.decision}\n\n"
    body += f"**Score :** {score}/100\n\n"

    if review.points_forts:
        body += "### Points forts\n\n"
        for point in review.points_forts:
            body += f"- {point}\n"

    if review.points_a_corriger:
        body += "\n### Points à corriger\n\n"
        for point in review.points_a_corriger:
            body += f"- {point}\n"

    if review.explications_pedagogiques:
        body += "\n### Explications pédagogiques\n\n"
        for point in review.explications_pedagogiques:
            body += f"- {point}\n"

    body += f"\n### Prochaine étape\n\n{review.next_step}\n"

    data = {
        "body": body,
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def approve_pr(pr_number):
    """Approuve la PR si le Lead a validé (score >= 80)."""
    if not REPO or not GITHUB_TOKEN:
        print("GITHUB_REPOSITORY ou GITHUB_TOKEN manquant.")
        return None

    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    data = {
        "body": "Mission approuvée par le Lead IA (score >= 80).",
        "event": "APPROVE",
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 422:
        print(
            "Approbation API non applicable (HTTP 422). "
            "Le commentaire de review est déjà posté. "
            "Le Lead IA a validé la mission."
        )
        return None
    response.raise_for_status()
    return response.json()


def main():
    if not PR_NUMBER:
        print("PR_NUMBER non défini.", file=sys.stderr)
        sys.exit(1)

    pr_number = int(PR_NUMBER)
    body = get_pr_body(pr_number)
    mission_id = extract_mission_id(body)

    if not mission_id:
        print(f"Mission ID non trouvé dans le body de la PR #{pr_number}.")
        generated_dir = Path("missions/mcp/generated")
        if generated_dir.exists():
            files = sorted(generated_dir.glob("mcp-*.json"))
            if files:
                mission_id = files[-1].stem

    if not mission_id:
        print("Impossible de déterminer la mission. Review annulée.")
        sys.exit(0)

    mission_file = Path(f"missions/mcp/generated/{mission_id}.json")
    if not mission_file.exists():
        print(f"Fichier mission introuvable : {mission_file}")
        sys.exit(0)

    mission = Mission.from_dict(json.loads(mission_file.read_text(encoding="utf-8")))
    changed_files = get_pr_files(pr_number)
    previous_reviews = get_previous_reviews(pr_number)

    cache = Cache(Path("data/cache/llm"))
    llm = load_llm_from_env(cache)
    review = review_mission(llm, mission, changed_files, previous_reviews)

    post_review(pr_number, review, review.score)

    if review.is_approved():
        approve_pr(pr_number)
        print(f"PR #{pr_number} approuvée.")
    else:
        print(f"PR #{pr_number} à revoir.")


if __name__ == "__main__":
    main()
