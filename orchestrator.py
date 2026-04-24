import os
import re
import sys
import time

# --- ABSOLUTE PATH RESOLUTION ---
# This ensures the OS can be run from ANY directory without corrupting memory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

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
    "Strategy": {"provider": "openai", "model": "o4-mini"},
    "Product Spec": {"provider": "openai", "model": "gpt-4o-mini"},
    "Design": {"provider": "anthropic", "model": "claude-sonnet-4-5"},
    "Engineering": {"provider": "anthropic", "model": "claude-sonnet-4-5"},
    "Growth Ops": {"provider": "openai", "model": "gpt-4o-mini"},
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
class LLMClient:
    def __init__(self):
        self.clients = {}
        if os.environ.get("OPENAI_API_KEY"):
            try:
                from openai import OpenAI

                self.clients["openai"] = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            except ImportError:
                print("❌ ERROR: openai package not found.")
                sys.exit(1)

        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                import anthropic

                self.clients["anthropic"] = anthropic.Anthropic(
                    api_key=os.environ.get("ANTHROPIC_API_KEY")
                )
            except ImportError:
                print("❌ ERROR: anthropic package not found.")
                sys.exit(1)

    def call(self, agent_name, system_prompt, user_prompt):
        if SMART_ROUTING and agent_name in MODEL_MAP:
            provider = MODEL_MAP[agent_name]["provider"]
            model = MODEL_MAP[agent_name]["model"]
        else:
            provider = DEFAULT_PROVIDER
            model = "gpt-4o" if provider == "openai" else "claude-sonnet-4-5"

        if provider not in self.clients:
            print(f"❌ ERROR: API key for {provider} not found. Cannot route {agent_name}.")
            sys.exit(1)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                start_time = time.time()

                if provider == "openai":
                    response = self.clients["openai"].chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                    )
                    text = response.choices[0].message.content
                    p_tokens = response.usage.prompt_tokens
                    c_tokens = response.usage.completion_tokens

                elif provider == "anthropic":
                    response = self.clients["anthropic"].messages.create(
                        model=model,
                        max_tokens=4096,
                        temperature=0.2,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_prompt}],
                    )
                    text = response.content[0].text
                    p_tokens = response.usage.input_tokens
                    c_tokens = response.usage.output_tokens

                elapsed = time.time() - start_time
                log_token_usage(agent_name, provider, model, p_tokens, c_tokens, elapsed)

                return text

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"\n❌ API ERROR({provider}-{model}) after {max_retries} attempts: {e}")
                    sys.exit(1)

                sleep_time = 2 ** (attempt + 1)
                print(f"\n⚠️ API Interruption ({provider}): {e}")
                print(f"🔄 Retrying in {sleep_time} seconds (Attempt {attempt + 1}/{max_retries}).")
                time.sleep(sleep_time)


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


def list_directory(dir_path):
    try:
        files = os.listdir(dir_path)
        if not files:
            return f"[SYSTEM NOTE: Directory {dir_path} is empty.]"
        return "\n".join([f"- {f}" for f in files])
    except FileNotFoundError:
        return f"[SYSTEM NOTE: Directory {dir_path} not found.]"


def assemble_context(agent_name):
    memory_path = os.path.join(DOCS_DIR, "company", "lessons_learned.md")
    context = f"\n\n--- SYSTEM MEMORY ---\n{read_file(memory_path)}\n"

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

        public_dir = os.path.join(BASE_DIR, "public")
        context += f"\n\n--- PUBLIC ASSETS ---\n{list_directory(public_dir)}"

    elif "Design" in agent_name:
        context += read_file(os.path.join(DOCS_DIR, "product", "current_run.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "flows.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "style_guide.md"))
        context += read_file(os.path.join(BASE_DIR, "src", "web", "lib", "content.ts"))

        public_dir = os.path.join(BASE_DIR, "public")
        context += f"\n\n--- PUBLIC ASSETS ---\n{list_directory(public_dir)}"

        blueprint = read_file(os.path.join(DOCS_DIR, "templates", "design_blueprint.md"))
        context += f"\n\n--- OUTPUT TEMPLATE ---\n{blueprint}"

    elif "Engineering" in agent_name:
        context += read_file(os.path.join(DOCS_DIR, "product", "current_run.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "architecture.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "adr", "README.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "flows.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "style_guide.md"))
        context += read_file(os.path.join(BASE_DIR, "src", "web", "lib", "content.ts"))

        public_dir = os.path.join(BASE_DIR, "public")
        context += f"\n\n--- PUBLIC ASSETS ---\n{list_directory(public_dir)}"

    elif "Ops" in agent_name:
        context += read_file(os.path.join(DOCS_DIR, "product", "current_run.md"))
        context += read_file(os.path.join(DOCS_DIR, "ops", "launch_checklist.md"))
        context += read_file(os.path.join(DOCS_DIR, "company", "scorecard.md"))

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
        system_prompt = read_file(os.path.join(SKILLS_DIR, skill_file))

        print(f"\n[🚀 Waking up {current_agent} Agent...]")

        payload = f"CONTEXT:\n{assemble_context(base_skill)}\n\nTASK:\n{current_prompt}"

        if verbose:
            print(f"🔎 [VERBOSE]: Sending {len(payload)} chars of context to {current_agent}...")
            print(f"--- PAYLOAD START ---\n{payload}\n--- PAYLOAD END ---")

        response = llm.call(
            base_skill,
            system_prompt,
            payload,
        )

        if verbose:
            print(f"\n[{current_agent} Output]:\n{response}\n")
        else:
            print(f"✅ {current_agent} successfully completed task.")

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
