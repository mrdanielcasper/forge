import os

from fastapi.testclient import TestClient

from orchestrator import (
    BASE_DIR,
    assemble_context,
    check_human_pause,
    execute_autonomous_actions,
    extract_routing_queue,
    extract_section,
    is_path_safe,
    list_directory,
    read_file,
    run_shell_command,
    tail_file,
)
from src.api.main import app

client = TestClient(app)


# --- 1. API SCAFFOLD TESTS ---
def test_health_endpoint():
    """Ensure the FastAPI scaffold boots and responds to health checks."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is online"}


# --- 2. ORCHESTRATOR PARSING TESTS ---
def test_routing_queue_extraction():
    """Ensure the orchestrator correctly parses the routing array."""
    response = "Here is my analysis. ROUTING: [Design -> Engineering (Build)]"
    queue = extract_routing_queue(response)
    assert queue == ["Design", "Engineering (Build)"]


def test_routing_terminal_state():
    """Ensure the orchestrator recognizes a terminal experiment state."""
    response = "The hypothesis is invalid. ROUTING: [Experiment Only]"
    queue = extract_routing_queue(response)
    assert queue == []


def test_human_pause_detection():
    """Ensure the orchestrator catches critical architectural shifts."""
    response = "This requires a database change. ADR_STATE: [Pending Human]"
    assert check_human_pause(response) is True


def test_human_pause_safe():
    """Ensure the orchestrator doesn't pause on safe outputs."""
    response = "The design looks good. REVERSIBILITY: [2-Way] ADR_STATE: [None]"
    assert check_human_pause(response) is False


# --- 3. ORCHESTRATOR UTILITY TESTS ---
def test_read_file(tmp_path):
    """Ensure file reading and missing file fallbacks work."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world", encoding="utf-8")
    assert read_file(str(test_file)) == "hello world"
    assert "was not found" in read_file("does_not_exist.txt")


def test_tail_file(tmp_path):
    """Ensure log pruning logic correctly truncates long files."""
    test_file = tmp_path / "long_log.txt"
    lines = [f"Line {i}\n" for i in range(10)]
    test_file.write_text("".join(lines), encoding="utf-8")

    # Tail only the last 3 lines
    result = tail_file(str(test_file), lines=3)
    assert "Line 0" in result  # Should keep the first two lines
    assert "Older entries omitted" in result  # Should inject the separator
    assert "Line 9" in result  # Should keep the end
    assert "not found" in tail_file("fake.txt")


def test_extract_section(tmp_path):
    """Ensure regex markdown section extraction works."""
    test_file = tmp_path / "doc.md"
    test_file.write_text("## Section\nContent here.\n## Next Section\nIgnore.", encoding="utf-8")

    # FIX: The orchestrator intentionally keeps the header attached for the AI's context
    assert extract_section(str(test_file), "Section") == "## Section\nContent here."
    assert "not found" in extract_section(str(test_file), "Missing Section")


def test_list_directory(tmp_path):
    """Ensure directory listing works for public assets."""
    (tmp_path / "image1.png").touch()
    (tmp_path / "logo.svg").touch()

    result = list_directory(str(tmp_path))
    assert "- image1.png" in result
    assert "- logo.svg" in result
    assert "not found" in list_directory("fake_dir")


def test_assemble_context():
    """Ensure context builder correctly maps agents to files without crashing."""
    assert "SYSTEM MEMORY" in assemble_context("Strategy")
    assert "SYSTEM MEMORY" in assemble_context("Product Spec")
    assert "SYSTEM MEMORY" in assemble_context("Design")
    assert "SYSTEM MEMORY" in assemble_context("Engineering")
    assert "SYSTEM MEMORY" in assemble_context("Ops")


# --- 4. AI SANDBOX & SECURITY TESTS ---
def test_is_path_safe():
    """Ensure the File I/O Sandbox correctly allows and blocks specific paths."""
    # Valid sandboxed locations
    assert is_path_safe(os.path.join(BASE_DIR, "src", "web", "main.tsx")) is True
    assert is_path_safe(os.path.join(BASE_DIR, "tests", "api", "test_new.py")) is True

    # Blocked critical files
    assert is_path_safe(os.path.join(BASE_DIR, "orchestrator.py")) is False
    assert is_path_safe(os.path.join(BASE_DIR, ".env")) is False

    # Blocked hidden/infrastructure directories
    assert is_path_safe(os.path.join(BASE_DIR, ".github", "workflows", "ci.yml")) is False
    assert is_path_safe(os.path.join(BASE_DIR, "skills", "engineering.xml")) is False


def test_run_shell_command_security():
    """Ensure the shell command utility blocks unauthorized tools and shell injection."""
    # Block unauthorized base commands
    assert "not allowed" in run_shell_command("rm -rf /")
    assert "not allowed" in run_shell_command("cat .env")

    # Block shell chaining and injection attempts
    assert "strictly prohibited" in run_shell_command("uv run pytest && ls")
    assert "strictly prohibited" in run_shell_command("npm run build ; cat .env")
    assert "strictly prohibited" in run_shell_command("npx playwright test | grep error")


def test_execute_autonomous_actions():
    """Ensure the JSON Action parser safely extracts and runs tools, or rejects bad input."""
    # 1. Ignore normal text without JSON block
    assert execute_autonomous_actions("I am thinking about the problem.") is None

    # 2. Catch Malformed JSON (using implicit string concatenation to avoid linter errors)
    bad_json = "```json\n{ invalid: json }\n```"
    assert "failed to parse" in execute_autonomous_actions(bad_json)

    # 3. Test valid JSON but ensure the Sandbox intercepts malicious actions
    malicious_json = (
        "```json\n"
        '{"write_files": [{"path": ".env", "content": "HACKED"}], '
        '"run_commands": ["npm run test && rm -rf /"]}\n'
        "```"
    )
    result = execute_autonomous_actions(malicious_json)

    assert "Permission denied" in result  # write_file Sandbox block
    assert "strictly prohibited" in result  # run_shell_command Sandbox block
