"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import json

N: int = 10  # Increased number of flashes to 10
sample_ms = 10.0
on_ms = 500

def random_time_interval(tmin: float, tmax: float) -> float:
    return random.uniform(tmin, tmax)

def blinker(N: int, led: Pin) -> None:
    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)

def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file."""
    with open(json_filename, "w") as f:
        json.dump(data, f)

def scorer(t: list[int | None]) -> None:
    """Evaluate and report player's performance."""
    misses = t.count(None)
    print(f"You missed the light {misses} / {len(t)} times")

    t_good = [x for x in t if x is not None]
    if t_good:
        minimum_time = min(t_good)
        maximum_time = max(t_good)
        average_time = sum(t_good) / len(t_good)
    else:
        minimum_time, maximum_time, average_time = None, None, None

    print(f"Response times - Min: {minimum_time}ms, Max: {maximum_time}ms, Avg: {average_time}ms")

    data = {
        "misses": misses,
        "total_flashes": len(t),
        "minimum_time": minimum_time,
        "maximum_time": maximum_time,
        "average_time": average_time
    }

    now = time.localtime()
    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"score-{now_str}.json"
    print("write", filename)

    write_json(filename, data)

if __name__ == "__main__":
    led = Pin(16, Pin.OUT)
    button = Pin(17, Pin.IN, Pin.PULL_UP)

    t: list[int | None] = []

    blinker(3, led)

    for i in range(N):
        time.sleep(random_time_interval(0.5, 5.0))
        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)

        led.low()

    blinker(5, led)

    scorer(t)