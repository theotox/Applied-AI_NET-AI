"""NetAI-Tools — FastAPI backend

A minimal chat interface that connects a user to an LLM armed with
real networking tools. This is Applied AI: the LLM decides which tool
to call, we execute it, and the result is synthesised into plain language.

Endpoints:
    POST /api/chat   — chat with the LLM (tools-enabled)
    GET  /api/health — health check
    GET  /api/tools  — list available tools (for frontend discovery)
"""

import logging
from typing import List

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm_client import call_llm_with_tools
from tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

with open("settings.yaml") as f:
    server_cfg = yaml.safe_load(f)["server"]

app = FastAPI(title="NetAI-Tools", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str       # "user" | "assistant" | "system"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ToolCallInfo(BaseModel):
    name: str
    arguments: dict
    result_preview: str

class ChatResponse(BaseModel):
    response: str
    tool_calls: List[ToolCallInfo] = []
    iterations: int = 0

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest):
    """Send a chat message. The LLM may call tools to answer."""
    raw_messages = [m.model_dump() for m in payload.messages]
    result = call_llm_with_tools(raw_messages, TOOL_SCHEMAS, TOOL_FUNCTIONS)
    return ChatResponse(
        response=result["response"],
        tool_calls=[ToolCallInfo(**tc) for tc in result["tool_calls"]],
        iterations=result["iterations"],
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/tools")
def list_tools():
    """Return available tool names and their schemas."""
    return {
        "tools": [
            {"name": s["function"]["name"], "description": s["function"]["description"]}
            for s in TOOL_SCHEMAS
        ]
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=server_cfg.get("host", "0.0.0.0"),
        port=server_cfg.get("port", 8000),
        reload=True,
        log_level="info",
    )
