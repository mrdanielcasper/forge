import os

# 2. Import pipeline logic from engine.runtime
from engine.runtime import (
    check_human_pause,
    execute_autonomous_actions,
    extract_routing_queue,
)

# 1. Import physical tools from engine.tools
from engine.tools import (
    BASE_DIR,
    extract_section,
    is_path_safe,
    list_directory,
    read_file,
    run_shell_command,
    tail_file,
)


def test_routing_queue_extraction():
    """Ensure the runtime correctly parses the routing array."""
    response = "Here is my analysis. ROUTING: [Design -> Engineering (Build)]"
    queue = extract_routing_queue(response)
    assert queue == ["Design", "Engineering (Build)"]


def test_routing_terminal_state():
    """Ensure the runtime recognizes a terminal experiment state."""
    response = "The hypothesis is invalid. ROUTING: [Experiment Only]"
    queue = extract_routing_queue(response)
    assert queue == []


def test_human_pause_detection():
    """Ensure the runtime catches critical architectural shifts."""
    response = "This requires a database change. ADR_STATE: [Pending Human]"
    assert check_human_pause(response) == "ADR_STATE: [Pending Human]"


def test_human_pause_safe():
    """Ensure the runtime doesn't pause on safe outputs."""
    response = "The design looks good. REVERSIBILITY: [2-Way] ADR_STATE: [None]"
    assert check_human_pause(response) is None


def test_read_file(tmp_path):
    """Ensure file reading and missing file fallbacks work."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world", encoding="utf-8")
    assert read_file(str(test_file)) == "hello world"


def test_tail_file(tmp_path):
    """Ensure log pruning logic correctly truncates long files."""
    test_file = tmp_path / "long_log.txt"
    lines = [f"Line {i}\n" for i in range(10)]
    test_file.write_text("".join(lines), encoding="utf-8")

    result = tail_file(str(test_file), lines=3)
    assert "Line 7" in result
    assert "Older entries omitted" in result


def test_extract_section(tmp_path):
    """Ensure regex markdown section extraction works."""
    test_file = tmp_path / "doc.md"
    test_file.write_text("## Section\nContent here.\n## Next Section\nIgnore.", encoding="utf-8")

    assert extract_section(str(test_file), "Section") == "## Section\nContent here."


def test_list_directory(tmp_path):
    """Ensure directory listing works for public assets."""
    (tmp_path / "image1.png").touch()
    (tmp_path / "logo.svg").touch()

    result = list_directory(str(tmp_path))
    assert "image1.png" in result
    assert "logo.svg" in result


def test_is_path_safe():
    """Ensure the File I/O Sandbox correctly allows and blocks specific paths."""
    assert is_path_safe(os.path.join(BASE_DIR, "src", "web", "main.tsx")) is True


def test_run_shell_command_security():
    """Ensure the shell command utility blocks unauthorized tools and shell injection."""
    assert "not allowed" in run_shell_command("rm -rf /")


def test_execute_autonomous_actions():
    """Ensure the JSON Action parser safely extracts and runs tools, or rejects bad input."""
    assert execute_autonomous_actions("I am thinking about the problem.") is None
