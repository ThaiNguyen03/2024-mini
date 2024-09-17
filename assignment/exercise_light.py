#!/usr/bin/env python3
"""
Use analog input with photocell
"""
import os
import time
import machine
import urequests
import config
FIREBASE_URL = config.FIREBASE_URL
API_KEY = config.FIREBASE_API_KEY
FIREBASE_TOKEN = config.FIREBASE_TOKEN
# GP28 is ADC2
ADC2 = 28

led = machine.Pin("LED", machine.Pin.OUT)
adc = machine.ADC(ADC2)

blink_period = 0.1

max_bright = 20000
min_bright = 10000
log_interval = 10
last_log_time = time.time()

def clip(value: float) -> float:
    """clip number to range [0, 1]"""
    if value < 0:
        return 0
    if value > 1:
        return 1
    return value

def log_to_firebase(value:int):
    timestamp = time.time()
    tm = time.gmtime(timestamp)
    timestamp_iso = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(
            tm[0], tm[1], tm[2], tm[3], tm[4], tm[5]
        )
    data = {
        "fields": {
            "value": {"integerValue": value},
            "time": {"timestampValue": timestamp_iso}
        }
    }
    try:
        response = urequests.post(FIREBASE_URL + '?access_token=' + FIREBASE_TOKEN, json=data)
        print("Response status:", response.status_code)
        print("Response text:", response.text)
        response.close()
    except Exception as e:
        print("An error occurred:", e)
while True:
    value = adc.read_u16()
    print(value)
    """
    need to clip duty cycle to range [0, 1]
    this equation will give values outside the range [0, 1]
    So we use function clip()
    """

    duty_cycle = clip((value - min_bright) / (max_bright - min_bright))
    led.high()
    time.sleep(blink_period * duty_cycle)

    led.low()
    time.sleep(blink_period * (1 - duty_cycle))
    current_time = time.time()
    
    if current_time - last_log_time >= log_interval:
        log_to_firebase(value)
        last_log_time = current_time
