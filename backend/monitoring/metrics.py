from analytics.agent_status import get_status
from analytics.latency_monitor import get_latencies
from analytics.memory_hits import get_memory_hits
from analytics.tool_calls import get_tool_stats


def prometheus_metrics():
    lines = [
        "# HELP omniresearch_agent_latency_seconds Last observed agent latency.",
        "# TYPE omniresearch_agent_latency_seconds gauge",
    ]

    for agent, latency in get_latencies().items():
        try:
            value = float(latency)
        except Exception:
            value = 0.0
        lines.append(f'omniresearch_agent_latency_seconds{{agent="{agent}"}} {value:.6f}')

    lines.extend([
        "# HELP omniresearch_tool_calls_total Tool calls by integration.",
        "# TYPE omniresearch_tool_calls_total counter",
    ])
    for tool, count in get_tool_stats().items():
        lines.append(f'omniresearch_tool_calls_total{{tool="{tool}"}} {int(count)}')

    memory_hits = get_memory_hits()
    if isinstance(memory_hits, dict):
        memory_hits = memory_hits.get("hits", 0)
    lines.extend([
        "# HELP omniresearch_memory_hits_total Semantic memory hits.",
        "# TYPE omniresearch_memory_hits_total counter",
        f"omniresearch_memory_hits_total {int(memory_hits or 0)}",
        "# HELP omniresearch_agent_status Agent status as numeric state.",
        "# TYPE omniresearch_agent_status gauge",
    ])

    status_map = {"idle": 0, "running": 1, "completed": 2, "failed": -1}
    for agent, status in get_status().items():
        lines.append(
            f'omniresearch_agent_status{{agent="{agent}",status="{status}"}} {status_map.get(str(status), 0)}'
        )

    return "\n".join(lines) + "\n"
