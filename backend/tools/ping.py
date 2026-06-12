import subprocess
import json
import re


def network_ping(target: str, count: int = 4) -> str:
    """Send ICMP ping to a target — the most fundamental network tool.

    This is the canonical example of "giving a tool to an LLM."
    The function runs a real system command, parses the output into
    structured JSON, and returns it as a string for the LLM to read.

    Args:
        target: IP address or hostname to ping.
        count:  Number of ICMP echo requests (default 4).

    Returns:
        JSON string with keys: target, alive, packet_loss_pct,
        latency_avg_ms, ttl, transmitted, received, raw_output.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), "-W", "2", target],
            capture_output=True, text=True, timeout=15,
        )
        output = result.stdout + result.stderr
        alive = result.returncode == 0

        loss_match = re.search(r'(\d+)% packet loss', output)
        rtt_match  = re.search(r'(?:min/avg/max(?:/mdev)?) = [\d.]+/([\d.]+)', output)
        ttl_match = re.search(r'ttl=(\d+)', output)
        pkt_match = re.search(r'(\d+) packets transmitted, (\d+) received', output)

        return json.dumps({
            "target": target,
            "alive": alive,
            "packet_loss_pct": int(loss_match.group(1)) if loss_match else None,
            "latency_avg_ms": float(rtt_match.group(1)) if rtt_match else None,
            "ttl": int(ttl_match.group(1)) if ttl_match else None,
            "transmitted": int(pkt_match.group(1)) if pkt_match else None,
            "received": int(pkt_match.group(2)) if pkt_match else None,
            "raw_output": output.strip(),
        }, indent=2)

    except subprocess.TimeoutExpired:
        return json.dumps({
            "target": target, "alive": False,
            "error": "Ping timed out after 15 seconds",
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "target": target, "alive": False,
            "error": str(e),
        }, indent=2)
