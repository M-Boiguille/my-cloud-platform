"""Chargement et formatage des prompts versionnés."""

from pathlib import Path

PROMPTS_DIR = Path("prompts")


def load_prompt(name: str) -> str:
    """Charge le contenu d'un prompt depuis prompts/{name}.txt."""
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt introuvable : {path}")
    return path.read_text(encoding="utf-8")


def format_prompt(name: str, variables: dict[str, str]) -> str:
    """Charge un prompt et injecte les variables par remplacement simple."""
    prompt = load_prompt(name)
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        prompt = prompt.replace(placeholder, value)
    return prompt
