# TypTalk - Voice to Text voor macOS

**Houd Right Option ingedrukt → spreek → laat los → tekst verschijnt!**

## ✅ Quick Start

```bash
cd ~/Documents/Repos/typtalk
./venv/bin/python3 typtalk.py &
```

## 🛑 Emergency Stop
```bash
pkill -f typtalk.py
```

## 📋 Na Mac Reboot
Start opnieuw met bovenstaande command, of installeer auto-start.

## 🔧 Vereiste Permissies

System Settings → Privacy & Security:
- Accessibility: Terminal + Python.app
- Input Monitoring: Terminal + Python.app
- Microfoon: Terminal

Python.app locatie: `/opt/homebrew/Cellar/python@3.14/.../Resources/Python.app`

## ⚙️ Configuratie

`config.py`: `HOTKEY = "alt_r"` (Right Option toets)

## 💡 Tips

- Houd Right Option minimaal 1 seconde ingedrukt
- Bij vastlopen: `pkill -f typtalk.py`

Gebouwd met Claude Code - Februari 2026
