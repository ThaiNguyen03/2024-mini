#!/usr/bin/env python3
"""
PWM Tone Generator

based on https://www.coderdojotc.org/micropython/sound/04-play-scale/
"""

import machine
import utime

# GP16 is the speaker pin
SPEAKER_PIN = 16

# create a Pulse Width Modulation Object on this pin
speaker = machine.PWM(machine.Pin(SPEAKER_PIN))

# Dictionary of Hz values for notes
NOTE_FREQUENCIES = {
    'C': 261,
    'D': 294,
    'E': 329,
    'F': 349,
    'G': 392,
    'A': 440,
    'B': 493,
    'C_high': 523
}

twinkle_notes = [
    ('C', 0.5), ('C', 0.5), ('G', 0.5), ('G', 0.5),
    ('A', 0.5), ('A', 0.5), ('G', 1.0),
    ('F', 0.5), ('F', 0.5), ('E', 0.5), ('E', 0.5),
    ('D', 0.5), ('D', 0.5), ('C', 1.0)
]

def playtone(frequency: float, duration: float) -> None:
    speaker.duty_u16(1000)
    speaker.freq(int(frequency))
    utime.sleep(duration)

def quiet():
    speaker.duty_u16(0)


for note, duration in twinkle_notes:
    frequency = NOTE_FREQUENCIES[note]
    print(f"Playing note: {note}, Frequency: {frequency} Hz")
    playtone(frequency, duration)
    quiet() 
    utime.sleep(0.1)

# Turn off the PWM
quiet()
