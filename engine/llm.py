import json
import os
import sys
import time

import litellm

from engine.tools import DOCS_DIR

# --- CONFIGURATION ---
SMART_ROUTING = os.environ.get("SMART_ROUTING", "true").lower() == "true"
DEFAULT_PROVIDER = os.environ.get("DEFAULT_PROVIDER", "openai").lower()

# --- SMART MODEL MAPPING (LiteLLM Format) ---
MODEL_MAP = {
    "Strategy": "openrouter/openai/gpt-4o-mini",
    "Product Spec": "openrouter/openai/gpt-4o",
    "Design": "openrouter/openai/gpt-4o",
    "Engineering": "openrouter/openai/gpt-4o",
    "Growth Ops": "openrouter/openai/gpt-4o-mini",
    "Ops": "openrouter/openai/gpt-4o-mini",
}


def log_token_usage(agent, provider, model, p_tokens, c_tokens, elapsed):
    """Appends token usage and latency telemetry to a local CSV artifact."""
    log_path = os.path.join(DOCS_DIR, "ops", "token_tracker.csv")
    file_exists = os.path.exists(log_path)
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write(
                    "timestamp,agent,provider,model,prompt_tokens,completion_tokens,latency_s\n"
                )
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp},{agent},{provider},{model},{p_tokens},{c_tokens},{elapsed:.2f}\n")
    except Exception as e:
        print(f"⚠️ Could not write telemetry log: {e}")


def log_jsonl_telemetry(
    agent, provider, model, p_tokens, c_tokens, elapsed, system_prompt, user_prompt, response
):
    """Appends full execution context to a JSONL file for Brain OS / Human debugging."""
    log_path = os.path.join(DOCS_DIR, "ops", "telemetry.jsonl")
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agent": agent,
            "provider": provider,
            "model": model,
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "latency_s": round(elapsed, 2),
            "response": response,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"⚠️ Could not write JSONL telemetry: {e}")


class LLMClient:
    def __init__(self):
        if SMART_ROUTING and not os.environ.get("OPENROUTER_API_KEY"):
            print("❌ SHIFT LEFT ERROR: SMART_ROUTING is ON, but OPENROUTER_API_KEY is missing.")
            sys.exit(1)

    def call(self, agent_name, system_prompt, user_prompt):
        if SMART_ROUTING and agent_name in MODEL_MAP:
            model = MODEL_MAP[agent_name]
        else:
            if DEFAULT_PROVIDER == "openai":
                model = "openai/gpt-4o-mini"
            elif DEFAULT_PROVIDER == "anthropic":
                model = "anthropic/claude-3-5-sonnet-latest"
            else:
                model = "openrouter/openai/gpt-4o-mini"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        start_time = time.time()
        try:
            response = litellm.completion(
                model=model, messages=messages, temperature=0.2, num_retries=3, drop_params=True
            )
            text = response.choices[0].message.content
            p_tokens = response.usage.prompt_tokens
            c_tokens = response.usage.completion_tokens
            elapsed = time.time() - start_time

            log_token_usage(agent_name, "litellm", model, p_tokens, c_tokens, elapsed)
            log_jsonl_telemetry(
                agent_name,
                "litellm",
                model,
                p_tokens,
                c_tokens,
                elapsed,
                system_prompt,
                user_prompt,
                text,
            )
            return text
        except litellm.AuthenticationError as e:
            print(f"\n❌ API AUTH FATAL ERROR ({model}): {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ API ERROR ({model}): {e}")
            sys.exit(1)
