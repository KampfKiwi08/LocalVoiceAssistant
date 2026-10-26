from modules.config import cfg
import time


timing_debug = cfg.get("debug", {}).get("timings", False)
start_time = 0
times_with_label = {}

def start():
    global start_time
    global times_with_label
    start_time = time.perf_counter()
    times_with_label = {}

def milestone(label: str):
    global start_time
    global times_with_label

    if timing_debug:
        if label not in times_with_label:
            times_with_label[label] = round(time.perf_counter() - start_time, 2)
            print("[time] " + label + ": " + str(times_with_label[label]))

def info(label: str, text: str):
    if timing_debug:
        print("[" + label + "] " + text)