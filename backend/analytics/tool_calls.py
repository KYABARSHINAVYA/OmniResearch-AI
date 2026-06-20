tool_stats = {}


def register_tool(tool_name):

    if tool_name not in tool_stats:

        tool_stats[tool_name] = 0

    tool_stats[tool_name] += 1


def get_tool_stats():

    return tool_stats