import pytest

from engine.cli import main


def test_cli_requires_prompt(monkeypatch, capsys):
    monkeypatch.setattr("engine.cli.boot", lambda: None)

    with pytest.raises(SystemExit) as excinfo:
        main([])  # No args

    captured = capsys.readouterr()
    assert "Usage: python engine/cli.py 'Your prompt'" in captured.out
    assert excinfo.value.code == 1


def test_cli_parses_flags_and_prompt(monkeypatch):
    monkeypatch.setattr("engine.cli.boot", lambda: None)

    called_args = {}

    def mock_run_os(prompt, flags):
        called_args["prompt"] = prompt
        called_args["flags"] = flags

    monkeypatch.setattr("engine.cli.run_os", mock_run_os)

    main(["--os-verbose", "Build a react app"])

    assert called_args["prompt"] == "Build a react app"
    assert "--os-verbose" in called_args["flags"]


def test_cli_reads_from_handoff(monkeypatch, tmp_path):
    monkeypatch.setattr("engine.cli.boot", lambda: None)

    # Mock DOCS_DIR
    import engine.cli

    monkeypatch.setattr(engine.cli, "DOCS_DIR", str(tmp_path))

    # Create mock handoff file
    ops_dir = tmp_path / "ops"
    ops_dir.mkdir()
    handoff_file = ops_dir / "handoff.md"
    handoff_file.write_text("STATUS: PAUSED\nPROMPT: Auto-resume from handoff", encoding="utf-8")

    called_args = {}
    monkeypatch.setattr("engine.cli.run_os", lambda p, f: called_args.update({"prompt": p}))

    main([])  # No args passed, should fall back to handoff file
    assert called_args["prompt"] == "Auto-resume from handoff"
