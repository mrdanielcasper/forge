import os
import re
import sys

from engine.runtime import check_dependencies, run_os
from engine.tools import BASE_DIR, DOCS_DIR

# --- SHIFT-LEFT: CROSS-PLATFORM ENCODING FIX ---
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def boot():
    """Extracts boot logic so tests can bypass dependency checks."""
    check_dependencies()
    try:
        from dotenv import load_dotenv

        load_dotenv(os.path.join(BASE_DIR, ".env"))
    except ImportError:
        print("❌ ERROR: python-dotenv package not found. Run: uv sync")
        sys.exit(1)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    boot()

    prompt = ""
    flags = []

    for arg in args:
        if arg.startswith("--"):
            flags.append(arg)
        elif not prompt:
            prompt = arg

    handoff_path = os.path.join(DOCS_DIR, "ops", "handoff.md")
    if not prompt and os.path.exists(handoff_path):
        with open(handoff_path, encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"PROMPT:\s*(.+)", content, re.IGNORECASE)
            if match:
                prompt = match.group(1).strip()

    if not prompt:
        print("Usage: python engine/cli.py 'Your prompt' [--os-verbose]")
        sys.exit(1)

    try:
        run_os(prompt, flags)
    except KeyboardInterrupt:
        print("\n\n🛑 OS Execution manually interrupted by user. Shutting down gracefully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
