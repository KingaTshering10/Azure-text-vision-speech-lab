"""Run from any working directory: python /path/to/02_text/chat_cli.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai_lab import chat


def main():
    messages = [{"role": "system", "content": "You are a concise, helpful information assistant."}]
    while True:
        try:
            text = input("You (quit to exit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if text.lower() == "quit":
            break
        if not text:
            continue
        candidate = messages + [{"role": "user", "content": text}]
        try:
            answer = chat(candidate)
        except Exception:
            print("Request failed. Check your root .env, deployment access, quota, and connectivity.")
            continue
        messages = candidate + [{"role": "assistant", "content": answer}]
        print("Assistant:", answer)


if __name__ == "__main__":
    main()
