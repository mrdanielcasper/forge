import json
from unittest.mock import MagicMock

from engine import llm
from engine.llm import LLMClient, log_jsonl_telemetry, log_token_usage


def test_log_token_usage(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "DOCS_DIR", str(tmp_path))

    log_token_usage("Engineering", "litellm", "gpt-4o", 100, 50, 1.25)

    log_file = tmp_path / "ops" / "token_tracker.csv"
    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8")
    assert "timestamp,agent,provider,model,prompt_tokens" in content
    assert "Engineering,litellm,gpt-4o,100,50,1.25" in content


def test_log_jsonl_telemetry(tmp_path, monkeypatch):
    monkeypatch.setattr(llm, "DOCS_DIR", str(tmp_path))

    log_jsonl_telemetry(
        "Design", "litellm", "gpt-4o", 10, 20, 1.5, "sys prompt", "user prompt", "output"
    )

    log_file = tmp_path / "ops" / "telemetry.jsonl"
    assert log_file.exists()

    data = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert data["agent"] == "Design"
    assert data["response"] == "output"
    assert data["prompt_tokens"] == 10


def test_llm_client_smart_routing(monkeypatch):
    # Bypass API key check
    monkeypatch.setattr(llm, "SMART_ROUTING", True)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    client = LLMClient()

    # Mock Litellm
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Mock LLM output"
    mock_response.usage.prompt_tokens = 5
    mock_response.usage.completion_tokens = 10

    mock_completion = MagicMock(return_value=mock_response)
    monkeypatch.setattr("litellm.completion", mock_completion)

    # Prevent telemetry from actually writing to disk during this test
    monkeypatch.setattr(llm, "log_token_usage", lambda *args: None)
    monkeypatch.setattr(llm, "log_jsonl_telemetry", lambda *args: None)

    result = client.call("Strategy", "System rules", "User task")

    assert result == "Mock LLM output"
    mock_completion.assert_called_once()

    # Assert it grabbed the correct model from MODEL_MAP for "Strategy"
    called_model = mock_completion.call_args[1]["model"]
    assert called_model == "openrouter/openai/gpt-4o-mini"
