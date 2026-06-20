import time

latencies = {}


def start_timer(agent):

    latencies[agent] = time.time()


def stop_timer(agent):

    elapsed = time.time() - latencies[agent]

    print(f"{agent}: {elapsed:.2f} sec")

    return elapsed


def save_latency(agent, elapsed):

    latencies[agent] = elapsed


def get_latencies():

    return latencies