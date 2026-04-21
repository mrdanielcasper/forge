import os
import re
import sys

# --- ENVIRONMENT & SECRETS ---
try:
    from dotenv import load_dotenv

    # Load environment variables from the .env file in the root directory
    load_dotenv()
except ImportError:
    print("❌ ERROR: python-dotenv package not found.")
    print("Run: pip install python-dotenv")
    sys.exit(1)

# --- CONFIGURATION ---
DOCS_DIR = "docs"
SKILLS_DIR = "skills"
MAX_CHAIN_STEPS = 10

# Toggles whether to use the cheapest/best model per agent, or a single default
SMART_ROUTING = os.environ.get("SMART_ROUTING", "true").lower() == "true"
DEFAULT_PROVIDER = os.environ.get("DEFAULT_PROVIDER", "openai").lower()

# --- SMART MODEL MAPPING ---
MODEL_MAP = {
    "Strategy": {"provider": "openai", "model": "o3-mini"},
    "Product Spec": {"provider": "openai", "model": "gpt-4o-mini"},
    "Design": {"provider": "anthropic", "model": "claude-3-7-sonnet-20250219"},
    "Engineering": {"provider": "anthropic", "model": "claude-3-7-sonnet-20250219"},
    "Growth Ops": {"provider": "openai", "model": "gpt-4o-mini"},
}


# --- LLM ABSTRACTION LAYER ---
class LLMClient:
    def __init__(self):
        self.clients = {}
        if os.environ.get("OPENAI_API_KEY"):
            try:
                from openai import OpenAI

                self.clients["openai"] = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            except ImportError:
                print("❌ ERROR: openai package not found. Run: pip install openai")
                sys.exit(1)

        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                import anthropic

                self.clients["anthropic"] = anthropic.Anthropic(
                    api_key=os.environ.get("ANTHROPIC_API_KEY")
                )
            except ImportError:
                print("❌ ERROR: anthropic package not found. Run: pip install anthropic")
                sys.exit(1)

    def call(self, agent_name, system_prompt, user_prompt):
        if SMART_ROUTING and agent_name in MODEL_MAP:
            provider = MODEL_MAP[agent_name]["provider"]
            model = MODEL_MAP[agent_name]["model"]
        else:
            provider = DEFAULT_PROVIDER
            model = "gpt-4o" if provider == "openai" else "claude-3-7-sonnet-20250219"

        if provider not in self.clients:
            print(
                f"❌ ERROR: API key for {provider} not found in .env file. Cannot route {agent_name}."
            )
            sys.exit(1)

        try:
            if provider == "openai":
                response = self.clients["openai"].chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response.choices[0].message.content

            elif provider == "anthropic":
                response = self.clients["anthropic"].messages.create(
                    model=model,
                    max_tokens=4096,
                    temperature=0.2,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return response.content[0].text

        except Exception as e:
            print(f"\n❌ API ERROR ({provider} - {model}): {e}")
            sys.exit(1)


llm = LLMClient()


# --- DETERMINISTIC CONTEXT PRUNING ---
def read_file(filepath):
    try:
        with open(filepath) as f:
            return f.read()
    except FileNotFoundError:
        return f"[SYSTEM NOTE: The file {filepath} was not found.]"


def tail_file(filepath, lines=50):
    try:
        with open(filepath) as f:
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
    pattern = rf"(?i)(##\s*{section_header}.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return f"[SYSTEM NOTE: Section '{section_header}' not found in {filepath}]"


def assemble_context(agent_name):
    context = f"\n\n--- SYSTEM MEMORY ---\n{read_file(f'{DOCS_DIR}/company/lessons_learned.md')}\n"

    if "Strategy" in agent_name:
        context += read_file(f"{DOCS_DIR}/company/thesis.md")
        context += tail_file(f"{DOCS_DIR}/company/feedback_log.md", lines=40)
        context += read_file(f"{DOCS_DIR}/company/scorecard.md")

    elif "Spec" in agent_name:
        context += extract_section(f"{DOCS_DIR}/product/backlog.md", "High Priority")
        context += read_file(f"{DOCS_DIR}/product/current_run.md")
        context += read_file(f"{DOCS_DIR}/product/architecture.md")  # Added Architecture awareness

    elif "Design" in agent_name:
        context += read_file(f"{DOCS_DIR}/product/current_run.md")
        context += read_file(f"{DOCS_DIR}/product/flows.md")

    elif "Engineering" in agent_name:
        context += read_file(f"{DOCS_DIR}/product/current_run.md")
        context += read_file(f"{DOCS_DIR}/product/architecture.md")  # Added Architecture awareness
        context += read_file(f"{DOCS_DIR}/product/adr/README.md")  # Added ADR awareness
        context += read_file(f"{DOCS_DIR}/product/flows.md")  # Added for Artifact Triangulation

    elif "Ops" in agent_name:
        context += read_file(f"{DOCS_DIR}/product/current_run.md")
        context += read_file(f"{DOCS_DIR}/ops/launch_checklist.md")
        context += read_file(f"{DOCS_DIR}/company/scorecard.md")

    return re.sub(r"\n{3,}", "\n\n", context)


# --- PARSING & ROUTING LOGIC ---
def check_human_pause(response_text):
    # Added ADR_STATE to the pause triggers
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
def run_os(user_input):
    print("=== Solopreneur OS Initialized ===")
    print(
        f"🔧 Smart Routing: {'ON' if SMART_ROUTING else 'OFF (Default: ' + DEFAULT_PROVIDER + ')'}"
    )

    agent_queue = []

    # Check for Fast-Tracks (HOTFIX or TEARDOWN)
    if "[HOTFIX]" in user_input:
        print("🚨 HOTFIX DETECTED. Bypassing Strategy and Spec.")
        agent_queue.append("Engineering")
        current_prompt = user_input.replace("[HOTFIX]", "").strip()
    elif "[TEARDOWN]" in user_input:
        print("🗑️ TEARDOWN DETECTED. Bypassing Strategy and Spec.")
        agent_queue.append("Engineering")
        current_prompt = (
            user_input.replace("[TEARDOWN]", "").strip()
            + "\n\nCRITICAL: Execute the Teardown mandate."
        )
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

        system_prompt = read_file(
            f"{SKILLS_DIR}/{skill_file_map.get(base_skill, 'engineering.xml')}"
        )

        print(f"\n[🚀 Waking up {current_agent} Agent...]")

        response = llm.call(
            base_skill,
            system_prompt,
            f"CONTEXT:\n{assemble_context(base_skill)}\n\nTASK:\n{current_prompt}",
        )
        print(f"\n[{current_agent} Output]:\n{response}\n")

        if check_human_pause(response):
            print("🛑 HUMAN IN THE LOOP TRIGGERED. Pipeline paused.")
            print(
                "Action Required: Review the output (e.g. approve the ADR or execute Teardown), update files manually, and run OS again."
            )
            sys.exit(0)

        new_queue = extract_routing_queue(response)
        if new_queue is not None:
            if len(new_queue) == 0:
                print("✅ Terminal state reached. Pipeline complete.")
                break
            agent_queue = new_queue
            print(f"🔀 New Routing Queue established: {' -> '.join(agent_queue)}")

        if not agent_queue:
            print("✅ Pipeline complete. No further routing instructions.")
            break

        print(f"⏭️ Handoff: Passing context to {agent_queue[0]}...")
        current_prompt = f"Process the output from the previous stage:\n{response}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py 'Your prompt'")
        sys.exit(1)
    run_os(sys.argv[1])
