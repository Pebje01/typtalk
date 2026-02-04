#!/usr/bin/env python3
"""Test welke toetsen pynput kan detecteren"""
from pynput import keyboard

print("=" * 60)
print("TOETS DETECTOR - Druk op verschillende toetsen")
print("=" * 60)
print("Probeer:")
print("  1. fn-toets")
print("  2. Rechter Option/Alt")
print("  3. F18 (fn via Karabiner)")
print("  4. Gewone letters")
print("")
print("Druk ESC om te stoppen")
print("=" * 60)

def on_press(key):
    try:
        print(f"✓ INGEDRUKT: {key}")
    except Exception as e:
        print(f"✗ Error bij press: {e}")

def on_release(key):
    try:
        print(f"  Losgelaten: {key}")
        if key == keyboard.Key.esc:
            print("\n→ ESC ingedrukt, stoppen...")
            return False
    except Exception as e:
        print(f"✗ Error bij release: {e}")

try:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
except Exception as e:
    print(f"\n✗✗✗ FOUT: {e}")
    print("\nDit betekent waarschijnlijk een permissie probleem!")
