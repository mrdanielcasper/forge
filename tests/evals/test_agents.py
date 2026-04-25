import os

import pytest

from orchestrator import LLMClient, assemble_context, read_file


@pytest.fixture(scope="module")
def client():
    """Provide a single LLMClient instance for the module to use."""
    return LLMClient()


@pytest.mark.eval
def test_strategy_rejects_out_of_scope_ideas(client):
    """EVAL: Strategy agent must ruthlessly kill ideas outside the thesis."""
    system_prompt = read_file(os.path.join("agents", "strategy.xml"))
    system_prompt += assemble_context("Strategy")

    user_prompt = "Let's pivot and build a 3D multiplayer mobile racing game."

    response = client.call("Strategy", system_prompt, user_prompt)

    assert "ROUTING: [None]" in response, "FAILED: Strategy failed to halt the pipeline."
    assert "write_files" not in response, "FAILED: Strategy tried to write a rejected idea."


@pytest.mark.eval
def test_strategy_accepts_valid_b2b_ideas(client):
    """EVAL: Strategy agent must accept and route valid B2B SaaS ideas."""
    system_prompt = read_file(os.path.join("agents", "strategy.xml"))
    system_prompt += assemble_context("Strategy")

    user_prompt = (
        "Users are complaining they can't export their user lists. "
        "Let's add a CSV export button to the admin dashboard."
    )

    response = client.call("Strategy", system_prompt, user_prompt)

    err_msg = "FAILED: Strategy failed to route a valid idea to Product Spec."
    assert "ROUTING: [Product Spec]" in response, err_msg
    assert "http://googleusercontent.com/immersive_entry_chip/0"
