"""Tool Registry — this is the ONLY file you edit to add new tools.

Pattern:
  1. Write the tool function in its own file (ping.py, curl.py, ...)
  2. Import it here
  3. Add it to TOOL_FUNCTIONS (name → callable)
  4. Add its OpenAI-style schema to TOOL_SCHEMAS

The LLM discovers tools through TOOL_SCHEMAS. The backend dispatches
calls through TOOL_FUNCTIONS. Everything else is automatic.
"""

from tools.ping import network_ping
from tools.curl import check_http

# ---------------------------------------------------------------------------
# Tool function map — name → Python callable
# ---------------------------------------------------------------------------
TOOL_FUNCTIONS = {
    "network_ping": network_ping,
    "check_http": check_http,
}

# ---------------------------------------------------------------------------
# Tool schemas — OpenAI function-calling format
# llama-server /v1/chat/completions understands this natively.
# ---------------------------------------------------------------------------
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "network_ping",
            "description": "Send ICMP ping to a target IP or hostname to check if it is reachable and measure round-trip latency and packet loss.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "IP address or hostname to ping (e.g. 8.8.8.8 or google.com)"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of ping packets to send (default: 4)",
                        "default": 4,
                    },
                },
                "required": ["target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_http",
            "description": "Perform an HTTP GET request to check if a web service is responding. Returns status code, timing, and a preview of the response body.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL to check (e.g. https://example.com/health)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Request timeout in seconds (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["url"],
            },
        },
    },
]
