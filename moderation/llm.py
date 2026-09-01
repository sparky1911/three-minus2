import json
import requests
import os



OLLAMA = os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/generate"

OLLAMA = "http://localhost:11434/api/generate"
MODEL = "llama-guard3:1b"


def llm_check(text: str, parent: str = "") -> tuple[str, str]:
    """Returns (decision, reason). decision is 'REJECT' or 'APPROVE'."""
    convo = f"Context: {parent}\n\n{text}" if parent else text

    r = requests.post(OLLAMA, json={
        "model": MODEL,
        "prompt": convo,
        "stream": False,
    }, timeout=20)
    r.raise_for_status()

    out = r.json()["response"].strip()
    first = out.splitlines()[0].strip().lower()

    if first.startswith("unsafe"):
        categories = out.splitlines()[1].strip() if len(out.splitlines()) > 1 else ""
        return "REJECT", categories
    return "APPROVE", ""