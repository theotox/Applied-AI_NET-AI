"""LLM Client — the core "tool loop" that connects the LLM to real tools.

This is THE key piece of Applied AI: the LLM decides which tool to call,
we execute it, and feed the result back for synthesis. The LLM never
touches the network directly — it thinks in terms of tool calls.

Flow per user message:
  1. Send conversation history + tool schemas to LLM
  2. LLM returns either text or a tool_call
  3. If tool_call: execute the Python function, append result as
     role="tool", go back to step 1
  4. If text: return it as the final response
  5. Hard limit of 10 iterations to prevent infinite loops
"""

import json
import logging
from typing import Optional

import httpx
import yaml

logger = logging.getLogger("netai.llm")

# Load settings once at import time
with open("settings.yaml") as f:
    _cfg = yaml.safe_load(f)["llm"]

LLM_HOST = _cfg["host"]
LLM_PORT = _cfg["port"]
LLM_MODEL = _cfg["model"]
LLM_TEMPERATURE = _cfg.get("temperature", 0.1)
LLM_MAX_TOKENS = _cfg.get("max_tokens", 8192)

MAX_ITERATIONS = 10


def _llm_call(messages: list, tools: Optional[list] = None) -> Optional[dict]:
    """Single round-trip to the LLM. Returns the choice message or None."""
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    try:
        url = f"http://{LLM_HOST}:{LLM_PORT}/v1/chat/completions"
        with httpx.Client(timeout=600.0, verify=False) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                logger.error(f"LLM HTTP {resp.status_code}: {resp.text[:300]}")
                return None
            choice = resp.json()["choices"][0]["message"]
            return {
                "role": choice.get("role", "assistant"),
                "content": choice.get("content") or "",
                "tool_calls": choice.get("tool_calls"),
            }
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None


def call_llm_with_tools(
    messages: list,
    tools: Optional[list] = None,
    tool_functions: Optional[dict] = None,
) -> dict:
    """The tool loop.

    Args:
        messages: Conversation history (will be mutated — system prompt
                  prepended if missing).
        tools:           OpenAI-style tool schemas list.
        tool_functions:  Dict mapping tool name → Python callable.

    Returns:
        {"response": str, "tool_calls": list[dict], "iterations": int}
    """
    # Ensure the system prompt is first
    if not any(m.get("role") == "system" for m in messages):
        messages.insert(0, {
            "role": "system",
            "content": (
                "You are NetAI, an expert network engineer assistant. "
                "You have access to networking tools (ping, curl, etc.) "
                "that let you probe real infrastructure. "
                "Use them to answer questions factually. "
                "Be concise, data-driven, and professional. "
                "Always report what you found — not what you assume."
            ),
        })

    if tool_functions is None:
        tool_functions = {}

    tool_calls_made = []
    final_response = None
    iteration = 0

    while iteration < MAX_ITERATIONS:
        iteration += 1
        logger.info(f"Tool loop iteration {iteration}/{MAX_ITERATIONS}")

        response = _llm_call(messages, tools)
        if not response:
            return {
                "response": "Error: Could not reach the LLM engine. Check that llama-server is running.",
                "tool_calls": tool_calls_made,
                "iterations": iteration,
            }

        # If the LLM responds with text (no tool call), we're done
        if not response.get("tool_calls"):
            content = (response.get("content") or "").strip()
            final_response = content or "Done. Anything else?"
            break

        # --- Tool call branch ---
        # Add the assistant message with tool_calls to history
        messages.append({
            "role": "assistant",
            "content": response.get("content") or "",
            "tool_calls": response["tool_calls"],
        })

        for tc in response["tool_calls"]:
            name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}

            logger.info(f"LLM called tool: {name}({args})")

            # Execute the tool function
            fn = tool_functions.get(name)
            if not fn:
                result = f"Error: Unknown tool '{name}'"
            else:
                try:
                    result = fn(**args)
                except Exception as e:
                    result = f"Error executing {name}: {e}"

            # Record for the response metadata
            tool_calls_made.append({
                "name": name,
                "arguments": args,
                "result_preview": str(result)[:300],
            })

            # Feed the result back to the LLM as a tool response
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", f"call_{iteration}_{name}"),
                "content": str(result)[:30000] if result else "No result",
            })

    if not final_response:
        final_response = "I completed the requested actions. What else would you like to check?"

    return {
        "response": final_response,
        "tool_calls": tool_calls_made,
        "iterations": iteration,
    }
