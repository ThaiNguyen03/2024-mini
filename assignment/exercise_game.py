"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import json
import config
import urequests

N: int = 5  # Increased number of flashes to 10
sample_ms = 10.0
on_ms = 500
FIREBASE_URL_GAME = config.FIREBASE_URL_GAME
FIREBASE_KEY = config.FIREBASE_API_KEY
FIREBASE_TOKEN = config.FIREBASE_TOKEN

def log_to_firebase(misses: int, total_flashes: int, minimum_time: float, maximum_time: float, average_time: float):
    timestamp = time.time()
    tm = time.gmtime(timestamp)
    timestamp_iso = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(
        tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]
    )
    data = {
        "fields": {
            "misses": {"integerValue": misses},
            "total_flashes": {"integerValue": total_flashes},
            "timestamp": {"timestampValue": timestamp_iso}
        }
    }

    if minimum_time is not None:
        data["fields"]["minimum_time"] = {"doubleValue": minimum_time}
    if maximum_time is not None:
        data["fields"]["maximum_time"] = {"doubleValue": maximum_time}
    if average_time is not None:
        data["fields"]["average_time"] = {"doubleValue": average_time}
    try:
        response = urequests.post(FIREBASE_URL_GAME + '?access_token=' + FIREBASE_TOKEN, json=data)
        print("Response status:", response.status_code)
        print("Response text:", response.text)
        response.close()
    except Exception as e:
        print("An error occurred:", e)
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
    log_to_firebase(misses, len(t), minimum_time, maximum_time, average_time)


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