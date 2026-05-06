import json
import os

import orchestrator
from orchestrator import (
    BASE_DIR,
    append_file,
    check_human_pause,
    execute_autonomous_actions,
    extract_routing_queue,
    get_active_artifacts,
    is_path_safe,
    list_directory,
    log_jsonl_telemetry,
    read_directory_contents,
    read_file,
    run_shell_command,
    tail_file,
    write_file,
)


def test_check_human_pause_returns_reason() -> None:
    adr_text = "The design is complete. ADR_STATE: [Pending Human] is required."
    assert check_human_pause(adr_text) == "ADR_STATE: [Pending Human]"

    circuit_text = "WARNING: CIRCUIT_BREAKER activated due to loop."
    assert check_human_pause(circuit_text) == "CIRCUIT_BREAKER"

    safe_text = "The component was built successfully. ROUTING: [Ops]"
    assert check_human_pause(safe_text) is None


def test_is_path_safe() -> None:
    assert is_path_safe(os.path.join(BASE_DIR, "src", "web", "main.tsx")) is True
    assert is_path_safe(os.path.join(BASE_DIR, "docs", "product", "brief.md")) is True
    assert is_path_safe(os.path.join(BASE_DIR, "render.yaml")) is True

    assert is_path_safe(os.path.join(BASE_DIR, ".env")) is False
    assert is_path_safe(os.path.join(BASE_DIR, "orchestrator.py")) is False
    assert is_path_safe(os.path.join(BASE_DIR, "package.json")) is False

    assert is_path_safe(os.path.join(BASE_DIR, "agents", "strategy.xml")) is False
    assert is_path_safe(os.path.join(BASE_DIR, ".git", "config")) is False

    assert is_path_safe(os.path.join(BASE_DIR, "src", "..", ".env")) is False


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
    assert "ERROR: The OS failed to parse your JSON action block" in result


def test_execute_autonomous_actions_no_json() -> None:
    assert execute_autonomous_actions("I am just talking with no code blocks.") is None


def test_run_shell_command_guardrails() -> None:
    assert "not allowed" in run_shell_command("rm -rf /")
    assert "prohibited" in run_shell_command("npm run build && rm -rf /")
    assert "prohibited" in run_shell_command("uv run pytest ; ls")
    assert "prohibited" in run_shell_command("npm run dev | grep error")


def test_file_io_security_blocks() -> None:
    assert "Permission denied" in write_file("../../restricted.txt", "data")
    assert "Permission denied" in append_file("../../restricted.txt", "data")


def test_deterministic_readers_file_not_found() -> None:
    assert "was not found" in read_file("nonexistent_file_12345.md")
    assert "not found" in tail_file("nonexistent_file_12345.md")
    assert "not found" in list_directory("nonexistent_dir_12345")


def test_extract_section(monkeypatch) -> None:
    monkeypatch.setattr(
        orchestrator, "read_file", lambda f: "## Header\nContent here\n## Next Header"
    )
    # FIX: The regex extracts the header itself alongside the content
    assert orchestrator.extract_section("dummy.md", "Header") == "## Header\nContent here"
    assert "not found" in orchestrator.extract_section("dummy.md", "Missing")


def test_execute_autonomous_actions_success(monkeypatch) -> None:
    calls = []

    monkeypatch.setattr(
        orchestrator,
        "write_file",
        lambda p, c: calls.append(("write", p, c)) or "[SUCCESS: write]",
    )
    monkeypatch.setattr(
        orchestrator,
        "append_file",
        lambda p, c: calls.append(("append", p, c)) or "[SUCCESS: append]",
    )
    monkeypatch.setattr(
        orchestrator,
        "run_shell_command",
        lambda cmd: calls.append(("run", cmd)) or "[SUCCESS: run]",
    )

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


def test_actual_file_io(tmp_path, monkeypatch) -> None:
    """Test real file operations securely using Pytest's tmp_path."""
    monkeypatch.setattr(orchestrator, "BASE_DIR", str(tmp_path))

    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    rel_path = "docs/test.md"
    test_file = tmp_path / rel_path

    # Test write_file
    res = write_file(rel_path, "Hello")
    assert "SUCCESS" in res
    assert test_file.read_text(encoding="utf-8") == "Hello"

    # Test append_file
    res = append_file(rel_path, "World")
    assert "SUCCESS" in res
    assert test_file.read_text(encoding="utf-8") == "Hello\nWorld\n"

    # Test read_file
    assert read_file(str(test_file)) == "Hello\nWorld\n"

    # Test tail_file
    long_content = "\n".join([f"Line {i}" for i in range(100)])
    test_file.write_text(long_content, encoding="utf-8")
    tail_res = tail_file(str(test_file), lines=5)
    assert "Line 99" in tail_res
    assert "Older entries omitted" in tail_res

    # Test list_directory
    list_res = list_directory(str(docs_dir))
    assert "- test.md" in list_res

    # Test read_directory_contents
    dir_res = read_directory_contents(str(docs_dir))
    # SHIFT-LEFT: Updated test to check for the new XML caching tags
    assert "--- FILE: test.md ---" in dir_res


def test_get_active_artifacts(tmp_path, monkeypatch) -> None:
    """Test artifact regex extraction from current_run.md."""
    monkeypatch.setattr(orchestrator, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(orchestrator, "DOCS_DIR", str(tmp_path / "docs"))

    run_path = tmp_path / "docs" / "product" / "current_run.md"
    run_path.parent.mkdir(parents=True)
    run_path.write_text(
        "## Linked Artifacts\n- docs/company/thesis.md\n- docs/product/flows.md\n## Next",
        encoding="utf-8",
    )

    artifacts = get_active_artifacts()
    assert "docs/company/thesis.md" in artifacts
    assert "docs/product/flows.md" in artifacts


def test_log_jsonl_telemetry(tmp_path, monkeypatch) -> None:
    """Ensure full execution telemetry is written to JSONL for observability."""
    monkeypatch.setattr(orchestrator, "DOCS_DIR", str(tmp_path / "docs"))

    log_jsonl_telemetry(
        "Engineering", "litellm", "gpt-4o", 10, 20, 1.5, "sys", "usr", "response_text"
    )

    log_file = tmp_path / "docs" / "ops" / "telemetry.jsonl"
    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8").strip()
    data = json.loads(content)

    assert data["agent"] == "Engineering"
    assert data["response"] == "response_text"
    assert data["prompt_tokens"] == 10


def test_auto_lint_file_python_success(mocker):
    """Ensure the Forge auto-linter correctly triggers ruff for Python files and passes."""
    from orchestrator import auto_lint_file

    mock_run = mocker.patch("subprocess.run")
    # Simulate a successful ruff check (exit code 0)
    mock_run.return_value = mocker.MagicMock(returncode=0)

    result = auto_lint_file("src/api/main.py")

    assert "✅ AUTO-LINT PASSED" in result
    mock_run.assert_called_once()

    # Prove it specifically chose the Python linter
    called_command = mock_run.call_args[0][0]
    assert "ruff" in called_command
    assert "check" in called_command


def test_auto_lint_file_typescript_failure(mocker):
    """Ensure the Forge auto-linter triggers biome for TS files and catches syntax errors."""
    from orchestrator import auto_lint_file

    mock_run = mocker.patch("subprocess.run")
    # Simulate a failed biome check (exit code 1)
    mock_run.return_value = mocker.MagicMock(
        returncode=1, stdout="Expected an identifier, but found '}'", stderr=""
    )

    result = auto_lint_file("src/web/components/ui/button.tsx")

    assert "⚠️ AUTO-LINT FAILED" in result
    assert "Expected an identifier" in result
    mock_run.assert_called_once()

    # Prove it specifically chose the Frontend linter
    called_command = mock_run.call_args[0][0]
    assert "biome" in called_command
    assert "check" in called_command
