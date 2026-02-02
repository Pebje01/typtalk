#!/usr/bin/env python3
"""
Hotkey Setup - Druk op een toets om deze als hotkey te registreren
"""

import json
from pathlib import Path
from pynput import keyboard
from pynput.keyboard import Key

HOTKEY_FILE = Path("~/.wispr_hotkey.json").expanduser()

# Mapping van Key objecten naar strings
KEY_NAMES = {
    Key.f1: "f1", Key.f2: "f2", Key.f3: "f3", Key.f4: "f4",
    Key.f5: "f5", Key.f6: "f6", Key.f7: "f7", Key.f8: "f8",
    Key.f9: "f9", Key.f10: "f10", Key.f11: "f11", Key.f12: "f12",
    Key.f13: "f13", Key.f14: "f14", Key.f15: "f15", Key.f16: "f16",
    Key.f17: "f17", Key.f18: "f18", Key.f19: "f19", Key.f20: "f20",
    Key.alt_r: "alt_r", Key.alt_l: "alt_l",
    Key.ctrl_r: "ctrl_r", Key.ctrl_l: "ctrl_l",
    Key.cmd_r: "cmd_r", Key.cmd_l: "cmd_l",
    Key.shift_r: "shift_r", Key.shift_l: "shift_l",
    Key.caps_lock: "caps_lock",
}

def save_hotkey(key_name: str):
    """Sla de hotkey op."""
    HOTKEY_FILE.write_text(json.dumps({"hotkey": key_name}))
    print(f"\n✓ Hotkey opgeslagen: {key_name}")
    print(f"  Bestand: {HOTKEY_FILE}")

def on_press(key):
    """Callback voor toets indrukken."""
    key_name = KEY_NAMES.get(key)

    if key_name:
        save_hotkey(key_name)
        return False  # Stop listener
    else:
        # Probeer de key naam te krijgen
        try:
            if hasattr(key, 'char') and key.char:
                print(f"\n✗ '{key.char}' is geen geldige hotkey.")
            else:
                print(f"\n✗ Deze toets wordt niet ondersteund.")
        except:
            print(f"\n✗ Deze toets wordt niet ondersteund.")

        print("  Gebruik een functietoets (F1-F20) of modifier (Option, Control, Command)")
        return None  # Blijf luisteren

def main():
    print("=" * 50)
    print("Wispr Clone - Hotkey Setup")
    print("=" * 50)
    print()
    print("Druk op de toets die je als hotkey wilt gebruiken:")
    print()
    print("Ondersteunde toetsen:")
    print("  - Functietoetsen: F1-F20")
    print("  - Rechter Option (alt_r)")
    print("  - Rechter Control (ctrl_r)")
    print("  - Rechter Command (cmd_r)")
    print("  - Caps Lock")
    print()
    print("TIP: Voor fn-toets, installeer Karabiner-Elements")
    print("     en map fn → F18")
    print()
    print("Wachten op toets...")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    print()
    print("Herstart wispr.py om de nieuwe hotkey te gebruiken.")

if __name__ == "__main__":
    main()
