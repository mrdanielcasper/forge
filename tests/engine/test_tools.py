import os

from engine import tools
from engine.tools import (
    BASE_DIR,
    append_file,
    auto_lint_file,
    get_active_artifacts,
    is_path_safe,
    read_directory_contents,
    read_file,
    run_shell_command,
    write_file,
)


def test_is_path_safe() -> None:
    assert is_path_safe(os.path.join(BASE_DIR, "src", "web", "main.tsx")) is True
    assert is_path_safe(os.path.join(BASE_DIR, "orchestrator.py")) is False
    assert is_path_safe(os.path.join(BASE_DIR, "agents", "strategy.xml")) is False


def test_run_shell_command_guardrails() -> None:
    assert "not allowed" in run_shell_command("rm -rf /")
    assert "prohibited" in run_shell_command("npm run build && rm -rf /")


def test_file_io_security_blocks() -> None:
    assert "Permission denied" in write_file("../../restricted.txt", "data")
    assert "Permission denied" in append_file("../../restricted.txt", "data")


def test_deterministic_readers_file_not_found() -> None:
    assert "was not found" in read_file("nonexistent_file_12345.md")


def test_extract_section(monkeypatch) -> None:
    monkeypatch.setattr(tools, "read_file", lambda f: "## Header\nContent here\n## Next Header")
    assert tools.extract_section("dummy.md", "Header") == "## Header\nContent here"


def test_actual_file_io(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(tools, "BASE_DIR", str(tmp_path))
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    rel_path = "docs/test.md"
    test_file = tmp_path / rel_path

    res = write_file(rel_path, "Hello")
    assert "SUCCESS" in res

    # Actually use the test_file variable to prove it wrote!
    assert test_file.read_text(encoding="utf-8") == "Hello"

    dir_res = read_directory_contents(str(docs_dir))
    assert '<document path="test.md">' in dir_res


def test_get_active_artifacts(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(tools, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(tools, "DOCS_DIR", str(tmp_path / "docs"))

    run_path = tmp_path / "docs" / "product" / "current_run.md"
    run_path.parent.mkdir(parents=True)
    run_path.write_text("## Linked Artifacts\n- docs/company/thesis.md", encoding="utf-8")

    artifacts = get_active_artifacts()
    assert "docs/company/thesis.md" in artifacts


def test_auto_lint_file_python_success(mocker):
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = mocker.MagicMock(returncode=0)
    result = auto_lint_file("src/api/main.py")
    assert "✅ AUTO-LINT PASSED" in result


def test_auto_lint_file_typescript_failure(mocker):
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value = mocker.MagicMock(returncode=1, stdout="Error", stderr="")
    result = auto_lint_file("src/web/components/ui/button.tsx")
    assert "⚠️ AUTO-LINT FAILED" in result


def test_run_shell_command_execution(monkeypatch):
    """Ensure run_shell_command correctly executes and wraps output in XML tags."""
    import subprocess
    from unittest.mock import MagicMock

    # Create a fake successful subprocess result
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "mocked test output"
    mock_result.stderr = ""

    # Intercept the real subprocess.run and return our fake result
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: mock_result)

    # Run a whitelisted command
    result = run_shell_command("pytest tests/")

    # Prove it worked and correctly wrapped the output in our Shift-Left XML tags
    assert "mocked test output" in result
    assert '<shell_output command="pytest tests/">' in result
