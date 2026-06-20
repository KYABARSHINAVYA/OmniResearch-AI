agent_status = {
    "planner": "idle",
    "research": "idle",
    "rag": "idle",
    "memory": "idle",
    "graph": "idle",
    "mcp": "idle",
    "writer": "idle",
    "reviewer": "idle"
}


def update_status(agent, status):
    agent_status[agent] = status


def get_status():
    return agent_status