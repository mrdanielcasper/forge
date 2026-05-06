import json
import os
import re
import sys

from engine.ast_parser import generate_project_stub
from engine.llm import SMART_ROUTING, LLMClient
from engine.tools import (
    AGENTS_DIR,
    BASE_DIR,
    DOCS_DIR,
    append_file,
    auto_lint_file,
    extract_section,
    get_active_artifacts,
    list_directory,
    read_file,
    run_shell_command,
    tail_file,
    write_file,
)

MAX_CHAIN_STEPS = 10


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


def assemble_context(agent_name):
    memory_path = os.path.join(DOCS_DIR, "company", "lessons_learned.md")
    context = f"\n\n--- SYSTEM MEMORY ---\n{read_file(memory_path)}\n"

    contracts_dir = os.path.join(DOCS_DIR, "product", "contracts")
    public_dir = os.path.join(BASE_DIR, "public")
    ui_components_dir = os.path.join(BASE_DIR, "src", "web", "components", "ui")

    # --- SHIFT-LEFT: AST OMNISCIENCE INJECTION ---
    try:
        src_dir = os.path.join(BASE_DIR, "src")
        if os.path.exists(src_dir):
            ast_map = generate_project_stub(src_dir)
            context += f"\n\n--- PROJECT ARCHITECTURE SKELETON (AST MAP) ---\n{ast_map}\n"
    except Exception as e:
        print(f"⚠️ Warning: AST Parsing failed. {e}")
    # ---------------------------------------------

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
        context += "\n\n--- ACTIVE FEATURE ARTIFACTS ---\n"
        for artifact_path in get_active_artifacts():
            fcontent = read_file(os.path.join(BASE_DIR, artifact_path))
            context += f'\n<document path="{artifact_path}">\n{fcontent}\n</document>\n'
        contract_list = list_directory(contracts_dir)
        context += f"\n\n--- EXISTING DATA CONTRACTS (Dir Listing) ---\n{contract_list}"
        context += f"\n\n--- PUBLIC ASSETS ---\n{list_directory(public_dir)}"
    elif "Design" in agent_name:
        context += read_file(os.path.join(DOCS_DIR, "product", "current_run.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "flows.md"))
        context += read_file(os.path.join(DOCS_DIR, "product", "style_guide.md"))
        context += read_file(os.path.join(BASE_DIR, "src", "web", "lib", "content.ts"))
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
        context += "\n\n--- ACTIVE FEATURE ARTIFACTS ---\n"
        for artifact_path in get_active_artifacts():
            fname = os.path.basename(artifact_path)
            fcontent = read_file(os.path.join(BASE_DIR, artifact_path))
            context += f"\n--- FILE: {fname} ---\n{fcontent}\n"
        teardown = read_file(os.path.join(DOCS_DIR, "templates", "teardown_manifest.md"))
        context += f"\n\n--- TEARDOWN TEMPLATE ---\n{teardown}"

    return re.sub(r"\n{3,}", "\n\n", context)


def check_human_pause(response_text):
    pauses = [
        r"REVERSIBILITY:\s*\[1-Way\]",
        r"DATA:\s*\[Pending",
        r"CIRCUIT_BREAKER",
        r"TEARDOWN:\s*\[Needed\]",
        r"ADR_STATE:\s*\[Pending Human\]",
    ]
    for p in pauses:
        match = re.search(p, response_text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def extract_routing_queue(response_text):
    match = re.search(r"ROUTING:\s*\[(.*?)\]", response_text, re.IGNORECASE)
    if match:
        raw_route = match.group(1).strip()
        if "None" in raw_route or "Experiment" in raw_route:
            return []
        return [agent.strip() for agent in raw_route.split("->")]
    return None


def execute_autonomous_actions(response_text):
    match = re.search(r"```json\s*\n(.*?)```", response_text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None

    try:
        json_str = match.group(1).strip().replace("\xa0", " ")
        payload = json.loads(json_str, strict=False)
        execution_logs = []

        if "write_files" in payload:
            for file_data in payload["write_files"]:
                path = file_data.get("path")
                content = file_data.get("content")
                if path and content:
                    result = write_file(path, content)
                    execution_logs.append(result)
                    if "SUCCESS" in result:
                        lint_result = auto_lint_file(path)
                        if lint_result:
                            execution_logs.append(lint_result)

        if "append_to_file" in payload:
            for file_data in payload["append_to_file"]:
                path = file_data.get("path")
                content = file_data.get("content")
                if path and content:
                    result = append_file(path, content)
                    execution_logs.append(result)
                    if "SUCCESS" in result:
                        lint_result = auto_lint_file(path)
                        if lint_result:
                            execution_logs.append(lint_result)

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


def run_os(user_input, flags=None):
    if flags is None:
        flags = []

    llm = LLMClient()
    verbose = "--os-verbose" in flags

    print("=== Solopreneur OS Initialized ===")
    print(f"🔧 Smart Routing: {'ON' if SMART_ROUTING else 'OFF'}")

    telemetry_path = os.path.join(DOCS_DIR, "ops", "telemetry.jsonl")
    os.makedirs(os.path.dirname(telemetry_path), exist_ok=True)
    with open(telemetry_path, "w", encoding="utf-8") as f:
        f.write("")

    agent_queue = []
    if "[HOTFIX]" in user_input:
        agent_queue.append("Engineering")
        current_prompt = user_input.replace("[HOTFIX]", "").strip()
    elif "[TEARDOWN]" in user_input:
        agent_queue.append("Engineering")
        teardown_prompt = user_input.replace("[TEARDOWN]", "").strip()
        current_prompt = teardown_prompt + "\n\nCRITICAL: Execute Teardown."
    elif "[START:" in user_input:
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

        action_results = execute_autonomous_actions(response)
        if action_results:
            print(f"\n🤖 [OS EXECUTING ACTIONS]:\n{action_results}")
            if "FAIL" in action_results or "Error" in action_results or "error" in action_results:
                print("⚠️ Tests failed! Routing back to Engineering for an autonomous fix...")
                agent_queue.insert(0, "Engineering")
                current_prompt = (
                    "Your previous code changes caused test failures. Fix them.\n\n"
                    f"TEST OUTPUT:\n{action_results}"
                )
                continue

        pause_reason = check_human_pause(response)
        if pause_reason:
            print("🛑 HUMAN IN THE LOOP TRIGGERED. Pipeline paused.")
            print(
                "💡 Action Required: Review the output (e.g. approve the ADR or execute "
                "Teardown), update files manually, and run OS again."
            )
            handoff_path = os.path.join(DOCS_DIR, "ops", "handoff.md")
            os.makedirs(os.path.dirname(handoff_path), exist_ok=True)
            with open(handoff_path, "w", encoding="utf-8") as f:
                f.write(f"STATUS: PAUSED\nREASON: {pause_reason}\nAGENT: {current_agent}\n")
            sys.exit(0)

        new_queue = extract_routing_queue(response)
        if new_queue is None:
            print("⚠️ WARNING: Agent forgot ROUTING tag. Halting to prevent loop.")
            break

        if len(new_queue) == 0:
            print("✅ Terminal state reached. Pipeline complete.")
            handoff_path = os.path.join(DOCS_DIR, "ops", "handoff.md")
            os.makedirs(os.path.dirname(handoff_path), exist_ok=True)
            with open(handoff_path, "w", encoding="utf-8") as f:
                f.write("STATUS: COMPLETE\nREASON: Terminal state reached.\n")
            break

        agent_queue = new_queue
        print(f"🔀 New Routing Queue established: {' -> '.join(agent_queue)}")
        print(f"⏭️ Handoff: Passing context to {agent_queue[0]}...")
        current_prompt = f"Process the output from the previous stage:\n{response}"
