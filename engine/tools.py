import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

# --- SHIFT-LEFT: Explicit whitelist of allowed command prefixes ---
ALLOWED_COMMANDS = (
    "npm run ",
    "uv run ",
    "pytest ",
    "npx ",  # Added for biome linting
)

# --- ABSOLUTE PATH RESOLUTION (Upgraded for /engine subdirectory) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
AGENTS_DIR = os.path.join(BASE_DIR, "engine", "agents")


def is_path_safe(filepath):
    try:
        target_path = Path(filepath).resolve()
        base_path = Path(BASE_DIR).resolve()

        allowed_dirs = [
            base_path / "src",
            base_path / "tests",
            base_path / "docs",
            base_path / "public",
        ]

        allowed_root_files = [
            base_path / "render.yaml",
            base_path / "vercel.json",
            base_path / "netlify.toml",
        ]

        restricted_files = [
            base_path / "orchestrator.py",
            base_path / ".env",
            base_path / "pyproject.toml",
            base_path / "package.json",
            base_path / "uv.lock",
        ]

        if target_path in restricted_files:
            return False
        if target_path in allowed_root_files:
            return True

        restricted_dirs = [base_path / ".github", base_path / ".git", base_path / "agents"]
        if any(target_path.is_relative_to(r_dir) for r_dir in restricted_dirs):
            return False

        return any(target_path.is_relative_to(d) for d in allowed_dirs)
    except Exception:
        return False


def write_file(filepath, content):
    abs_path = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath
    if not is_path_safe(abs_path):
        return f"[ERROR: Permission denied to write to {filepath}]"
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[SUCCESS: File written to {filepath}]"
    except Exception as e:
        return f"[ERROR: Failed to write to {filepath} - {e}]"


def append_file(filepath, content):
    abs_path = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath
    if not is_path_safe(abs_path):
        return f"[ERROR: Permission denied to append to {filepath}]"
    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        prefix = ""
        if os.path.exists(abs_path):
            with open(abs_path, encoding="utf-8") as f:
                current_content = f.read()
                if current_content and not current_content.endswith("\n"):
                    prefix = "\n"
        with open(abs_path, "a", encoding="utf-8") as f:
            f.write(prefix + content + "\n")
        return f"[SUCCESS: Data appended to {filepath}]"
    except Exception as e:
        return f"[ERROR: Failed to append to {filepath} - {e}]"


def run_shell_command(command: str) -> str:
    if not command.startswith(ALLOWED_COMMANDS):
        return f"[ERROR: Command '{command}' not allowed.]"
    if any(char in command for char in ["&", "|", ";", ">", "<"]):
        return "[ERROR: Shell injection prohibited.]"
    try:
        args = shlex.split(command)
        if os.name == "nt":
            executable = shutil.which(args[0])
            if executable:
                args[0] = executable

        print(f"    $ {command}")
        # noqa: S603 tells the linter we have explicitly sandboxed this input
        result = subprocess.run(  # noqa: S603
            args, capture_output=True, text=True, encoding="utf-8", timeout=60, shell=False
        )

        def truncate_output(text, max_len=1000):
            if not text or len(text) <= max_len:
                return text
            half = max_len // 2
            return text[:half] + f"\n\n.[TRUNCATED {len(text) - max_len} CHARS].\n\n" + text[-half:]

        output = truncate_output(result.stdout.strip())
        error = truncate_output(result.stderr.strip())
        combined_output = output
        if error:
            combined_output += f"\nSTDERR:\n{error}"

        if len(combined_output) > 8000:
            combined_output = (
                combined_output[:8000] + "\n\n...[SYSTEM WARNING: Truncated at 8000 chars]..."
            )

        # SHIFT-LEFT: XML Caching Tags applied to shell outputs
        if result.returncode == 0:
            final_out = combined_output if combined_output else "SUCCESS"
            return f'<shell_output command="{command}">\n{final_out}\n</shell_output>'
        else:
            return f'<shell_error command="{command}">\n{combined_output}\n</shell_error>'
    except subprocess.TimeoutExpired:
        return "[ERROR: Command timed out after 60 seconds.]"
    except Exception as e:
        return f"[ERROR: Command execution failed - {str(e)}]"


def read_file(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[SYSTEM NOTE: The file {filepath} was not found.]"


def tail_file(filepath, lines=50):
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.readlines()
            if len(content) > lines:
                return "".join(
                    content[:2] + ["\n...[Older entries omitted]...\n\n"] + content[-lines:]
                )
            return "".join(content)
    except FileNotFoundError:
        return f"[SYSTEM NOTE: {filepath} not found.]"


def extract_section(filepath, section_header):
    content = read_file(filepath)
    safe_header = re.escape(section_header)
    pattern = rf"(?i)(##\s*{safe_header}.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return f"[SYSTEM NOTE: Section '{section_header}' not found in {filepath}]"


def get_active_artifacts():
    run_path = os.path.join(DOCS_DIR, "product", "current_run.md")
    content = read_file(run_path)
    artifacts = []
    paths = re.findall(r"(?:docs|src|public|tests)[a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+", content)
    for path in set(paths):
        if "current_run.md" not in path:
            artifacts.append(path)
    return artifacts


def list_directory(dir_path):
    try:
        files = os.listdir(dir_path)
        ignored = {".git", "node_modules", ".venv", "__pycache__"}
        filtered_files = [f for f in files if not (f.endswith(".csv") or f in ignored)]
        if not filtered_files:
            return f"[SYSTEM NOTE: Directory {dir_path} is empty or only contains ignored files.]"
        return "\n".join([f"- {f}" for f in filtered_files])
    except FileNotFoundError:
        return f"[SYSTEM NOTE: Directory {dir_path} not found.]"


def read_directory_contents(dir_path):
    content = ""
    try:
        ignored = {".git", "node_modules", ".venv", "__pycache__"}
        for filename in os.listdir(dir_path):
            if filename.endswith(".csv") or filename in ignored:
                continue
            if filename.endswith(".md"):
                filepath = os.path.join(dir_path, filename)
                content += f'\n<document path="{filename}">\n{read_file(filepath)}\n</document>\n'
    except FileNotFoundError:
        pass
    return content


def auto_lint_file(filepath):
    abs_path = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath
    ext = os.path.splitext(abs_path)[1]
    args = []
    if ext == ".py":
        args = ["uv", "run", "ruff", "check", "--no-cache", abs_path]
    elif ext in [".ts", ".tsx", ".js", ".jsx"]:
        args = ["npx", "biome", "check", abs_path]
    else:
        return None

    if os.name == "nt":
        executable = shutil.which(args[0])
        if executable:
            args[0] = executable

    try:
        # noqa: S603 tells the linter we have explicitly sandboxed this input
        result = subprocess.run(  # noqa: S603
            args, capture_output=True, text=True, encoding="utf-8", timeout=30, shell=False
        )
        if result.returncode != 0:
            return (
                f"[⚠️ AUTO-LINT FAILED on {filepath}]:\n"
                f"{result.stdout}\n{result.stderr}\n"
                "Fix this syntax error before proceeding."
            )
        return f"[✅ AUTO-LINT PASSED for {filepath}]"
    except Exception as e:
        return f"[⚠️ AUTO-LINT EXECUTION ERROR on {filepath}]: {e}"
