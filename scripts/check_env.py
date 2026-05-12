"""Check optional live-mode environment variables for Lab 24."""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def masked(value: str | None) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "set"
    return f"{value[:4]}...{value[-4:]}"


def main() -> int:
    load_dotenv(ROOT / ".env")
    checks = {
        "OPENAI_API_KEY": "Live RAGAS test generation/evaluation and LLM judge",
        "GROQ_API_KEY": "Groq-hosted Prompt Guard 2 or legacy Llama Guard",
        "HUGGINGFACEHUB_API_TOKEN": "Gated Hugging Face Llama Guard download",
        "LANGSMITH_API_KEY": "Optional eval tracing",
        "LANGFUSE_PUBLIC_KEY": "Optional eval tracing",
        "LANGFUSE_SECRET_KEY": "Optional eval tracing",
    }

    print(f"LAB24_MODE={os.getenv('LAB24_MODE', 'offline')}")
    for key, purpose in checks.items():
        print(f"{key}: {masked(os.getenv(key))} - {purpose}")

    if os.getenv("LAB24_MODE", "offline").lower() == "live" and not os.getenv("OPENAI_API_KEY"):
        print("Live mode needs OPENAI_API_KEY for RAGAS/OpenAI judge workflows.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
