import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# --- ABSOLUTE PATH RESOLUTION ---
# This ensures the OS can be run from ANY directory without corrupting memory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
AGENTS_DIR = os.path.join(BASE_DIR, "agents")


# --- PRE-FLIGHT BOOT CHECK ---
# Ensures users have installed dependencies before the OS tries to run automated tests
def check_dependencies():
    missing = []
    if not os.path.exists(os.path.join(BASE_DIR, "node_modules")):
        missing.append("npm install")
    if not os.path.exists(os.path.join(BASE_DIR, ".venv")):
        missing.append("uv sync")

    if missing:
        print("🛑 OS BOOT FAILED: Missing dependencies.")
        print("Please run the following commands before starting the OS:")
        for cmd in missing:
            print(f"  $ {cmd}")
        sys.exit(1)


check_dependencies()

# --- ENVIRONMENT & SECRETS ---
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    print("❌ ERROR: python-dotenv package not found. Run: pip install python-dotenv")
    sys.exit(1)

# --- CONFIGURATION ---
MAX_CHAIN_STEPS = 10
SMART_ROUTING = os.environ.get("SMART_ROUTING", "true").lower() == "true"
DEFAULT_PROVIDER = os.environ.get("DEFAULT_PROVIDER", "openai").lower()

# --- SMART MODEL MAPPING ---
MODEL_MAP = {
    "Strategy": {"provider": "openrouter", "model": "openai/gpt-4o-mini"},
    "Product Spec": {"provider": "openrouter", "model": "openai/gpt-4o"},
    "Design": {"provider": "openrouter", "model": "openai/gpt-4o"},
    "Engineering": {"provider": "openrouter", "model": "openai/gpt-4o"},
    "Growth Ops": {"provider": "openrouter", "model": "openai/gpt-4o-mini"},
}


# --- TELEMETRY LOGGER ---
def log_token_usage(agent, provider, model, p_tokens, c_tokens, elapsed):
    """Appends token usage and latency telemetry to a local CSV artifact."""
    log_path = os.path.join(DOCS_DIR, "ops", "token_tracker.csv")
    file_exists = os.path.exists(log_path)

    try:
        # Ensure the ops directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write(
                    "timestamp,agent,provider,model,prompt_tokens,completion_tokens,latency_s\n"
                )

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp},{agent},{provider},{model},{p_tokens},{c_tokens},{elapsed:.2f}\n")
    except Exception as e:
        print(f"⚠️ Could not write telemetry log: {e}")


# --- API CLIENT ---
PROVIDERS = {
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "headers": lambda key: {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "prompt-caching-2024-07-31",
            "content-type": "application/json",
        },
        "body": lambda model, system, user: {
            "model": model,
            "max_tokens": 4096,
            "temperature": 0.2,
            "system": [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},  # Native Prompt Caching
                }
            ],
            "messages": [{"role": "user", "content": user}],
        },
        "extract": lambda r: r["content"][0]["text"],
        # Combine standard tokens with cached tokens so telemetry remains accurate
        "tokens": lambda r: (
            r["usage"].get("input_tokens", 0) + r["usage"].get("cache_read_input_tokens", 0),
            r["usage"].get("output_tokens", 0),
        ),
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        "body": lambda model, system, user: {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        },
        "extract": lambda r: r["choices"][0]["message"]["content"],
        "tokens": lambda r: (
            r["usage"].get("prompt_tokens", 0),
            r["usage"].get("completion_tokens", 0),
        ),
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Solopreneur OS",
        },
        "body": lambda model, system, user: {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        },
        "extract": lambda r: r["choices"][0]["message"]["content"],
        "tokens": lambda r: (
            r["usage"].get("prompt_tokens", 0),
            r["usage"].get("completion_tokens", 0),
        ),
    },
}


class LLMClient:
    def __init__(self):
        self.keys = {
            "openai": os.environ.get("OPENAI_API_KEY"),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
            "openrouter": os.environ.get("OPENROUTER_API_KEY"),
        }

    def call(self, agent_name, system_prompt, user_prompt):
        if SMART_ROUTING and agent_name in MODEL_MAP:
            provider = MODEL_MAP[agent_name]["provider"]
            model = MODEL_MAP[agent_name]["model"]
        else:
            provider = DEFAULT_PROVIDER
            if provider == "openai":
                model = "gpt-4o"
            elif provider == "anthropic":
                model = "claude-3-5-sonnet-latest"
            else:
                # --- TRACER BULLET FIX: RELIABLE & CHEAP ---
                # Swapped the rate-limited free tier for gpt-4o-mini.
                # Extremely reliable, and costs ~ $0.01 per run.
                model = "openai/gpt-4o-mini"

        if provider not in PROVIDERS:
            print(f"❌ ERROR: Provider '{provider}' is not configured in PROVIDERS dict.")
            sys.exit(1)

        api_key = self.keys.get(provider)
        if not api_key:
            print(f"❌ ERROR: API key for {provider} not found in .env.")
            sys.exit(1)

        config = PROVIDERS[provider]
        max_retries = 3

        for attempt in range(max_retries):
            try:
                start_time = time.time()

                req = urllib.request.Request(  # noqa: S310
                    config["url"],
                    data=json.dumps(config["body"](model, system_prompt, user_prompt)).encode(
                        "utf-8"
                    ),
                    headers=config["headers"](api_key),
                    method="POST",
                )

                with urllib.request.urlopen(req, timeout=120) as response:  # noqa: S310
                    result = json.loads(response.read().decode("utf-8"))
                    text = config["extract"](result)
                    p_tokens, c_tokens = config["tokens"](result)

                elapsed = time.time() - start_time
                log_token_usage(agent_name, provider, model, p_tokens, c_tokens, elapsed)

                return text

            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8") if e.fp else str(e)
                if attempt == max_retries - 1:
                    print(
                        f"\n❌ API FATAL ERROR ({provider} - {model}): HTTP {e.code} - {error_body}"
                    )
                    sys.exit(1)

                sleep_time = 2 ** (attempt + 1)
                print(f"\n⚠️ API Interruption ({provider}): HTTP {e.code} - {error_body}")
                print(
                    f"🔄 Retrying in {sleep_time} seconds (Attempt {attempt + 1}/{max_retries})..."
                )
                time.sleep(sleep_time)

            except Exception as e:
                if attempt == max_retries - 1:
                    print(
                        f"\n❌ API FATAL ERROR ({provider} - {model}) "
                        f"after {max_retries} attempts: {e}"
                    )
                    sys.exit(1)

                sleep_time = 2 ** (attempt + 1)
                print(f"\n⚠️ API Interruption ({provider}): {e}")
                print(
                    f"🔄 Retrying in {sleep_time} seconds (Attempt {attempt + 1}/{max_retries})..."
                )
                time.sleep(sleep_time)


# --- AI FILE I/O SANDBOX ---
def is_path_safe(filepath):
    """Sandbox security guardrail to prevent path traversal and unauthorized edits."""
    try:
        target_path = Path(filepath).resolve()
        base_path = Path(BASE_DIR).resolve()

        # Whitelisted directories
        allowed_dirs = [
            base_path / "src",
            base_path / "tests",
            base_path / "docs",
            base_path / "public",
        ]

        # Whitelist specific root files for PaaS Deployments
        allowed_root_files = [
            base_path / "render.yaml",
            base_path / "vercel.json",
            base_path / "netlify.toml",
        ]

        # Blacklisted files (never touch these even if they are in base_path)
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

        # Blacklisted directories
        restricted_dirs = [
            base_path / ".github",
            base_path / ".git",
            base_path / "agents",  # AI cannot rewrite its own brain!
        ]

        if any(target_path.is_relative_to(restricted_dir) for restricted_dir in restricted_dirs):
            return False

        # Must be in whitelist
        return any(target_path.is_relative_to(d) for d in allowed_dirs)

    except Exception:
        return False


def write_file(filepath, content):
    """Safely writes content to a file if it passes the sandbox checks."""
    abs_path = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath

    if not is_path_safe(abs_path):
        print(f"🛑 SECURITY BLOCK: AI attempted to write to unauthorized path: {filepath}")
        return f"[ERROR: Permission denied to write to {filepath}]"

    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[SUCCESS: File written to {filepath}]"
    except Exception as e:
        return f"[ERROR: Failed to write to {filepath} - {e}]"


def append_file(filepath, content):
    """Safely appends content to a file if it passes the sandbox checks."""
    abs_path = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath

    if not is_path_safe(abs_path):
        print(f"🛑 SECURITY BLOCK: AI attempted to write to unauthorized path: {filepath}")
        return f"[ERROR: Permission denied to append to {filepath}]"

    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        # Check if the file currently exists and ensure it ends with a newline
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


def run_shell_command(command):
    """Executes an isolated shell command and returns stdout/stderr."""
    # Strict whitelist of allowed automated commands
    allowed_prefixes = [
        "uv run pytest",
        "npm run",
        "npx playwright",
        "npx @biomejs/biome",
        "mv ",
        "move ",
    ]

    if not any(command.startswith(prefix) for prefix in allowed_prefixes):
        print(f"🛑 SECURITY BLOCK: AI attempted unauthorized command: {command}")
        return f"[ERROR: Command '{command}' not allowed.]"

    # Prevent shell injection (e.g., 'uv run pytest && rm -rf /')
    dangerous_chars = ["&&", ";", "|", ">", "<", "`", "$"]
    if any(char in command for char in dangerous_chars):
        print(f"🛑 SECURITY BLOCK: AI attempted shell chaining/injection: {command}")
        return "[ERROR: Shell chaining and redirection are strictly prohibited.]"

    # Safely parse the command string into a list for subprocess
    try:
        args = shlex.split(command, posix=False)
    except ValueError as e:
        return f"[ERROR: Failed to parse command - {str(e)}]"

    try:
        print(f"⚙️ Running automated tests: {command}")
        result = subprocess.run(  # noqa: S603
            args,  # <-- Pass the list, not the raw string
            shell=False,  # <-- THE CRITICAL FIX
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )

        output = result.stdout if result.returncode == 0 else result.stderr
        output = output.strip() if output else "[Process completed with no output]"

        # --- NEW FIX: Bounded Shell Logs to prevent API Token Burn ---
        if len(output) > 3000:
            output = (
                output[:500]
                + "\n\n...[SYSTEM NOTE: MASSIVE LOG TRUNCATED TO SAVE TOKENS]...\n\n"
                + output[-2500:]
            )

        return output
    except Exception as e:
        return f"[ERROR: Command execution failed - {e}]"


# --- DETERMINISTIC CONTEXT PRUNING ---
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
    # Safely escape the header to prevent regex injection crashes
    safe_header = re.escape(section_header)
    pattern = rf"(?i)(##\s*{safe_header}.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return f"[SYSTEM NOTE: Section '{section_header}' not found in {filepath}]"


def get_active_artifacts():
    """Parses current_run.md to extract the exact file paths of active artifacts."""
    run_path = os.path.join(DOCS_DIR, "product", "current_run.md")
    content = read_file(run_path)

    # Find all lines in the Linked Artifacts section that contain a file path
    # e.g., "- Brief: docs/product/briefs/feature.md"
    artifacts = []

    # Extract the block between Linked Artifacts and the next header
    match = re.search(r"(?i)## Linked Artifacts(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if match:
        block = match.group(1)
        # Find anything that looks like a markdown path
        paths = re.findall(r"(docs/[a-zA-Z0-9_/-]+\.md)", block)
        for path in paths:
            # Make sure we don't accidentally load current_run.md inside current_run.md
            if "current_run.md" not in path:
                artifacts.append(path)

    return artifacts


def list_directory(dir_path):
    try:
        files = os.listdir(dir_path)
        # --- HYGIENE PATCH: Filter out junk from context ---
        ignored = {".git", "node_modules", ".venv", "__pycache__"}
        filtered_files = [f for f in files if not (f.endswith(".csv") or f in ignored)]

        if not filtered_files:
            return f"[SYSTEM NOTE: Directory {dir_path} is empty or only contains ignored files.]"
        return "\n".join([f"- {f}" for f in filtered_files])
    except FileNotFoundError:
        return f"[SYSTEM NOTE: Directory {dir_path} not found.]"


def read_directory_contents(dir_path):
    """Reads and concatenates safe files in a given directory."""
    content = ""
    try:
        ignored = {".git", "node_modules", ".venv", "__pycache__"}
        for filename in os.listdir(dir_path):
            # --- HYGIENE PATCH: Skip token-wasting files ---
            if filename.endswith(".csv") or filename in ignored:
                continue

            # Currently restricted to markdown
            if filename.endswith(".md"):
                filepath = os.path.join(dir_path, filename)
                content += f"\n--- FILE: {filename} ---\n{read_file(filepath)}\n"
    except FileNotFoundError:
        pass
    return content


def assemble_context(agent_name):
    memory_path = os.path.join(DOCS_DIR, "company", "lessons_learned.md")
    context = f"\n\n--- SYSTEM MEMORY ---\n{read_file(memory_path)}\n"

    # Define dynamic paths
    contracts_dir = os.path.join(DOCS_DIR, "product", "contracts")
    public_dir = os.path.join(BASE_DIR, "public")
    ui_components_dir = os.path.join(BASE_DIR, "src", "web", "components", "ui")

    if "Strategy" in agent_name:
        context += read_file(os.path.join(DOCS_DIR, "company", "thesis.md"))
        feedback_log_path = os.path.join(DOCS_DIR, "company", "feedback_log.md")
        context += tail_file(feedback_log_path, lines=40)
        context += read_file(os.path.join(DOCS_DIR, "company", "scorecard.md"))

    elif "Spec" in agent_name:
        backlog_path = os.path.join(DOCS_DIR, "product", "backlog.md")
        context += extract_section(backlog_path, "High Priority")
        context += read_file(os.path.join(DOCS_DIR, "product", "current_run.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "architecture.md"))

        # --- CONTEXT FUNNELING: Only load active artifacts ---
        context += "\n\n--- ACTIVE FEATURE ARTIFACTS ---\n"
        for artifact_path in get_active_artifacts():
            fname = os.path.basename(artifact_path)
            fcontent = read_file(os.path.join(BASE_DIR, artifact_path))
            context += f"\n--- FILE: {fname} ---\n{fcontent}\n"

        # List existing contracts instead of reading all their contents to save tokens
        contract_list = list_directory(contracts_dir)
        context += f"\n\n--- EXISTING DATA CONTRACTS (Dir Listing) ---\n{contract_list}"
        context += f"\n\n--- PUBLIC ASSETS ---\n{list_directory(public_dir)}"

    elif "Design" in agent_name:
        context += read_file(os.path.join(DOCS_DIR, "product", "current_run.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "flows.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "style_guide.md"))
        context += read_file(os.path.join(BASE_DIR, "src", "web", "lib", "content.ts"))

        # --- CONTEXT FUNNELING: Only load active artifacts ---
        context += "\n\n--- ACTIVE FEATURE ARTIFACTS ---\n"
        for artifact_path in get_active_artifacts():
            fname = os.path.basename(artifact_path)
            fcontent = read_file(os.path.join(BASE_DIR, artifact_path))
            context += f"\n--- FILE: {fname} ---\n{fcontent}\n"

        context += f"\n\n--- PUBLIC ASSETS ---\n{list_directory(public_dir)}"
        context += f"\n\n--- AVAILABLE UI COMPONENTS ---\n{list_directory(ui_components_dir)}"

        blueprint = read_file(os.path.join(DOCS_DIR, "templates", "design_blueprint.md"))
        context += f"\n\n--- OUTPUT TEMPLATE ---\n{blueprint}"

    elif "Engineering" in agent_name:
        context += read_file(os.path.join(DOCS_DIR, "product", "current_run.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "architecture.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "adr", "README.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "flows.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "style_guide.md"))
        context += read_file(os.path.join(BASE_DIR, "src", "web", "lib", "content.ts"))

        # --- CONTEXT FUNNELING: Only load active artifacts ---
        context += "\n\n--- ACTIVE FEATURE ARTIFACTS ---\n"
        for artifact_path in get_active_artifacts():
            fname = os.path.basename(artifact_path)
            fcontent = read_file(os.path.join(BASE_DIR, artifact_path))
            context += f"\n--- FILE: {fname} ---\n{fcontent}\n"

        context += f"\n\n--- PUBLIC ASSETS ---\n{list_directory(public_dir)}"
        context += f"\n\n--- AVAILABLE UI COMPONENTS ---\n{list_directory(ui_components_dir)}"

        teardown = read_file(os.path.join(DOCS_DIR, "templates", "teardown_manifest.md"))
        context += f"\n\n--- TEARDOWN TEMPLATE ---\n{teardown}"

    elif "Ops" in agent_name:
        context += read_file(os.path.join(DOCS_DIR, "product", "current_run.md"))
        context += read_file(os.path.join(DOCS_DIR, "ops", "launch_checklist.md"))
        context += read_file(os.path.join(DOCS_DIR, "company", "scorecard.md"))

        # --- CONTEXT FUNNELING: Only load active artifacts ---
        context += "\n\n--- ACTIVE FEATURE ARTIFACTS ---\n"
        for artifact_path in get_active_artifacts():
            fname = os.path.basename(artifact_path)
            fcontent = read_file(os.path.join(BASE_DIR, artifact_path))
            context += f"\n--- FILE: {fname} ---\n{fcontent}\n"

        teardown = read_file(os.path.join(DOCS_DIR, "templates", "teardown_manifest.md"))
        context += f"\n\n--- TEARDOWN TEMPLATE ---\n{teardown}"

    return re.sub(r"\n{3,}", "\n\n", context)


# --- PARSING & ROUTING LOGIC ---
def check_human_pause(response_text):
    pauses = [
        r"REVERSIBILITY:\s*\[1-Way\]",
        r"DATA:\s*\[Pending",
        r"CIRCUIT_BREAKER",
        r"TEARDOWN:\s*\[Needed\]",
        r"ADR_STATE:\s*\[Pending Human\]",
    ]
    return any(re.search(p, response_text, re.IGNORECASE) for p in pauses)


def extract_routing_queue(response_text):
    match = re.search(r"ROUTING:\s*\[(.*?)\]", response_text, re.IGNORECASE)
    if match:
        raw_route = match.group(1).strip()
        if "None" in raw_route or "Experiment" in raw_route:
            return []
        return [agent.strip() for agent in raw_route.split("->")]
    return None


def execute_autonomous_actions(response_text):
    """Scans the AI's response for a JSON payload and executes the sandbox tools."""
    # Look for a JSON block explicitly tagged for the OS
    match = re.search(r"```json\s*\n(.*?)```", response_text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None  # No automated actions requested

    try:
        json_str = match.group(1).strip().replace("\xa0", " ")
        payload = json.loads(json_str, strict=False)

        execution_logs = []

        # 1. Execute File Writes (Sledgehammer)
        if "write_files" in payload:
            for file_data in payload["write_files"]:
                path = file_data.get("path")
                content = file_data.get("content")
                if path and content:
                    result = write_file(path, content)
                    execution_logs.append(result)

        # 1.5 Execute File Appends (Scalpel)
        if "append_to_file" in payload:
            for file_data in payload["append_to_file"]:
                path = file_data.get("path")
                content = file_data.get("content")
                if path and content:
                    result = append_file(path, content)
                    execution_logs.append(result)

        # 2. Execute Shell Commands (Testing/Linting)
        if "run_commands" in payload:
            for cmd in payload["run_commands"]:
                result = run_shell_command(cmd)
                execution_logs.append(f"$ {cmd}\n{result}")

        return "\n\n".join(execution_logs)

    except json.JSONDecodeError as e:
        return (
            f"[ERROR: The OS failed to parse your JSON action block. Python Error: {e}. "
            "Ensure you are properly escaping quotes and newlines inside your Markdown strings.]"
        )
    except Exception as e:
        return f"[ERROR: OS Execution failed - {e}]"


# --- CORE EXECUTION LOOP ---
def run_os(user_input, flags=None):
    if flags is None:
        flags = []

    # Lazy initialization so the module can be imported for testing
    llm = LLMClient()
    verbose = "--os-verbose" in flags

    print("=== Solopreneur OS Initialized ===")
    print(f"🔧 Smart Routing: {'ON' if SMART_ROUTING else 'OFF'}")

    agent_queue = []

    if "[HOTFIX]" in user_input:
        agent_queue.append("Engineering")
        current_prompt = user_input.replace("[HOTFIX]", "").strip()
    elif "[TEARDOWN]" in user_input:
        agent_queue.append("Engineering")
        teardown_prompt = user_input.replace("[TEARDOWN]", "").strip()
        current_prompt = teardown_prompt + "\n\nCRITICAL: Execute Teardown."
    elif "[START:" in user_input:
        # Allow CEO to bypass Strategy and start at any agent
        match = re.search(r"\[START:\s*(.*?)\]", user_input)
        if match:
            agent_queue.append(match.group(1).strip())
            current_prompt = user_input
        else:
            agent_queue.append("Strategy")
            current_prompt = user_input
    else:
        agent_queue.append("Strategy")
        current_prompt = user_input

    step_count = 0

    while agent_queue:
        step_count += 1
        if step_count > MAX_CHAIN_STEPS:
            print("\n🛑 ERROR: Maximum execution steps reached.")
            sys.exit(1)

        current_agent = agent_queue.pop(0)
        base_skill = current_agent.split("(")[0].strip()

        skill_file_map = {
            "Strategy": "strategy.xml",
            "Product Spec": "product_spec.xml",
            "Design": "design.xml",
            "Engineering": "engineering.xml",
            "Growth Ops": "growth_ops.xml",
            "Ops": "growth_ops.xml",
        }

        skill_file = skill_file_map.get(base_skill, "engineering.xml")
        skill_prompt = read_file(os.path.join(AGENTS_DIR, skill_file))

        print(f"\n[🚀 Waking up {current_agent} Agent...]")

        # Combine the Skill XML and the Context into a single System Prompt for maximum caching
        full_system_prompt = f"{skill_prompt}\n\nCONTEXT:\n{assemble_context(base_skill)}"
        user_task = f"TASK:\n{current_prompt}"

        if verbose:
            print(
                f"🔎 [VERBOSE]: Sending {len(full_system_prompt)} chars of "
                f"cached system context to {current_agent}..."
            )
            print(f"--- USER TASK ---\n{user_task}\n-----------------")

        response = llm.call(
            base_skill,
            full_system_prompt,
            user_task,
        )

        if verbose:
            print(f"\n[{current_agent} Output]:\n{response}\n")
        else:
            print(f"✅ {current_agent} successfully completed task.")

        # --- AUTONOMOUS EXECUTION LOOP ---
        action_results = execute_autonomous_actions(response)

        if action_results:
            print(f"\n🤖 [OS EXECUTING ACTIONS]:\n{action_results}")

            # If a test failed, feed it immediately back to the Engineering agent!
            if "FAIL" in action_results or "Error" in action_results or "error" in action_results:
                print("⚠️ Tests failed! Routing back to Engineering for an autonomous fix...")
                agent_queue.insert(0, "Engineering")
                current_prompt = (
                    "Your previous code changes caused test failures. Fix them.\n\n"
                    f"TEST OUTPUT:\n{action_results}"
                )
                continue  # Skip the routing queue and immediately re-run the agent

        # ---------------------------------

        if check_human_pause(response):
            print("🛑 HUMAN IN THE LOOP TRIGGERED. Pipeline paused.")
            print(
                "💡 Action Required: Review the output (e.g. approve the ADR or execute "
                "Teardown), update files manually, and run OS again."
            )
            sys.exit(0)

        new_queue = extract_routing_queue(response)

        if new_queue is None:
            print("⚠️ WARNING: Agent forgot ROUTING tag. Halting to prevent loop.")
            break

        if len(new_queue) == 0:
            print("✅ Terminal state reached. Pipeline complete.")
            break

        agent_queue = new_queue
        print(f"🔀 New Routing Queue established: {' -> '.join(agent_queue)}")
        print(f"⏭️ Handoff: Passing context to {agent_queue[0]}...")
        current_prompt = f"Process the output from the previous stage:\n{response}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py 'Your prompt' [--os-verbose]")
        sys.exit(1)

    # sys.argv[1] is exactly your prompt. sys.argv[2:] catches any flags.
    try:
        run_os(sys.argv[1], sys.argv[2:])
    except KeyboardInterrupt:
        print("\n\n🛑 OS Execution manually interrupted by user. Shutting down gracefully.")
        sys.exit(0)
