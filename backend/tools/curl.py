import json
import httpx


def check_http(url: str, timeout: int = 10) -> str:
    """Perform an HTTP GET request — like curl but in Python.

    Useful for checking if web services, APIs, and health endpoints
    are responding. Returns status code, timing, and a preview of
    the response body.

    Args:
        url:     Full URL to check (e.g. https://example.com/health).
        timeout: Request timeout in seconds (default 10).

    Returns:
        JSON string with keys: url, status_code, ok, content_type,
        content_preview, elapsed_seconds, or error details.
    """
    try:
        with httpx.Client(verify=False, timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url)
            preview = resp.text[:200].strip().replace("\n", " ") if resp.text else ""
            return json.dumps({
                "url": url,
                "status_code": resp.status_code,
                "ok": resp.is_success,
                "content_type": resp.headers.get("content-type", "unknown"),
                "content_length": len(resp.text),
                "content_preview": preview,
                "elapsed_seconds": round(resp.elapsed.total_seconds(), 2),
            }, indent=2)
    except httpx.ConnectError:
        return json.dumps({
            "url": url, "ok": False,
            "error": "Connection refused — could not reach host",
        }, indent=2)
    except httpx.TimeoutException:
        return json.dumps({
            "url": url, "ok": False,
            "error": f"Request timed out after {timeout}s",
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "url": url, "ok": False,
            "error": str(e),
        }, indent=2)
