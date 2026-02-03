#!/usr/bin/env python3
"""
Test of fn toets (via F18) gedetecteerd wordt
"""

from pynput import keyboard
from pynput.keyboard import Key

print("=" * 50)
print("Test: fn toets detectie (via Karabiner F18)")
print("=" * 50)
print()
print("Druk op de fn toets (linksonder op je keyboard)")
print("Als Karabiner correct is ingesteld, zie je 'F18 detected!'")
print()
print("Druk Ctrl+C om te stoppen")
print("-" * 50)

def on_press(key):
    try:
        # Check verschillende varianten
        if hasattr(key, 'name'):
            print(f"Key pressed: {key.name}")

        if key == Key.f18:
            print("✓ F18 DETECTED! fn toets werkt via Karabiner!")
            return False  # Stop na eerste detectie

    except AttributeError:
        if hasattr(key, 'char'):
            print(f"Char pressed: {key.char}")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

print()
print("Test voltooid!")
