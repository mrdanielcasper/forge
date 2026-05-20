import json

import pytest

from engine import runtime
from engine.llm import log_jsonl_telemetry
from engine.runtime import (
    check_human_pause,
    execute_autonomous_actions,
    extract_routing_queue,
)


def test_check_human_pause_returns_reason() -> None:
    adr_text = "The design is complete. ADR_STATE: [Pending Human] is required."
    assert check_human_pause(adr_text) == "ADR_STATE: [Pending Human]"

    circuit_text = "WARNING: CIRCUIT_BREAKER activated due to loop."
    assert check_human_pause(circuit_text) == "CIRCUIT_BREAKER"

    safe_text = "The component was built successfully. ROUTING: [Ops]"
    assert check_human_pause(safe_text) is None


def test_extract_routing_queue() -> None:
    assert extract_routing_queue("ROUTING: [Spec -> Engineering -> Ops]") == [
        "Spec",
        "Engineering",
        "Ops",
    ]
    assert extract_routing_queue("ROUTING: [Engineering]") == ["Engineering"]
    assert extract_routing_queue("ROUTING: [None]") == []
    assert extract_routing_queue("ROUTING: [Experiment]") == []
    assert extract_routing_queue("Some random text without routing") is None


def test_execute_autonomous_actions_invalid_json() -> None:
    bad_response = "```json\n { this is not valid json } \n```"
    result = execute_autonomous_actions(bad_response)
    assert result is not None
    assert "ERROR: The OS failed to parse" in result


def test_execute_autonomous_actions_no_json() -> None:
    assert execute_autonomous_actions("I am just talking with no code blocks.") is None


def test_execute_autonomous_actions_success(monkeypatch) -> None:
    calls = []

    # Patch the tools directly inside the runtime module where they are executed
    monkeypatch.setattr(
        runtime, "write_file", lambda p, c: calls.append(("write", p, c)) or "[SUCCESS: write]"
    )
    monkeypatch.setattr(
        runtime, "append_file", lambda p, c: calls.append(("append", p, c)) or "[SUCCESS: append]"
    )
    monkeypatch.setattr(
        runtime, "run_shell_command", lambda cmd: calls.append(("run", cmd)) or "[SUCCESS: run]"
    )
    monkeypatch.setattr(runtime, "auto_lint_file", lambda p: None)
    json_payload = """```json
    {
        "write_files": [{"path": "test.txt", "content": "hello"}],
        "append_to_file": [{"path": "test.txt", "content": " world"}],
        "run_commands": ["npm run format"]
    }
    ```"""

    result = execute_autonomous_actions(json_payload)

    assert "[SUCCESS: write]" in result
    assert "[SUCCESS: append]" in result
    assert "$ npm run format" in result
    assert ("write", "test.txt", "hello") in calls
    assert ("append", "test.txt", " world") in calls
    assert ("run", "npm run format") in calls


def test_log_jsonl_telemetry(tmp_path, monkeypatch) -> None:
    from engine import llm

    monkeypatch.setattr(llm, "DOCS_DIR", str(tmp_path / "docs"))

    log_jsonl_telemetry(
        "Engineering", "litellm", "gpt-4o", 10, 20, 1.5, "sys", "usr", "response_text"
    )

    log_file = tmp_path / "docs" / "ops" / "telemetry.jsonl"
    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8").strip()
    data = json.loads(content)

    assert data["agent"] == "Engineering"
    assert data["response"] == "response_text"


def test_check_dependencies(monkeypatch):
    """Ensure the boot checker accurately halts the OS if node_modules or .venv are missing."""
    # Test Failure Path
    monkeypatch.setattr("os.path.exists", lambda p: False)
    with pytest.raises(SystemExit):
        runtime.check_dependencies()

    # Test Success Path
    monkeypatch.setattr("os.path.exists", lambda p: True)
    runtime.check_dependencies()  # Should not raise an error


def test_assemble_context_branches(monkeypatch, tmp_path):
    """Dynamically test every context injection branch to ensure it doesn't crash."""
    monkeypatch.setattr(runtime, "DOCS_DIR", str(tmp_path))
    monkeypatch.setattr(runtime, "BASE_DIR", str(tmp_path))

    # Run through all possible agent branches to hit 100% of the if/elif conditions
    for agent in ["Strategy", "Spec", "Design", "Engineering", "Ops"]:
        context = runtime.assemble_context(agent)
        assert isinstance(context, str)
        assert "--- SYSTEM MEMORY ---" in context


def test_run_os_execution_loop(monkeypatch, tmp_path):
    """Test the entire main execution loop without actually calling Claude."""
    monkeypatch.setattr(runtime, "DOCS_DIR", str(tmp_path))
    monkeypatch.setattr(runtime, "AGENTS_DIR", str(tmp_path))
    monkeypatch.setattr(runtime, "BASE_DIR", str(tmp_path))

    # Create a dummy LLM that immediately routes to 'None' so the loop exits after 1 step
    class DummyLLM:
        def call(self, agent_name, sys_prompt, user_prompt):
            return "Here is my mock analysis. ROUTING: [None]"

    monkeypatch.setattr(runtime, "LLMClient", DummyLLM)

    # 1. Test standard routing
    runtime.run_os("Hello OS", ["--os-verbose"])

    # 2. Test HOTFIX routing bypass
    runtime.run_os("[HOTFIX] The database is down")

    # 3. Test TEARDOWN routing
    runtime.run_os("[TEARDOWN] Remove the new feature")

    # 4. Test START OVERRIDE routing
    runtime.run_os('<forge_instruction route="Design">Make it pretty</forge_instruction>')
