memory_hits = 0


def increment_memory_hits():

    global memory_hits

    memory_hits += 1


def get_memory_hits():

    return memory_hits