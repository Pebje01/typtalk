# TypTalk - Voice to Text for macOS

Privacy-first voice-to-text tool voor macOS. Houd de fn toets ingedrukt, spreek, en de tekst wordt automatisch getypt waar je cursor staat.

## ✨ Features

- 🎤 **fn toets hotkey** - Houd fn in, spreek, laat los
- ⚡ **Supersnel** - 0.8s transcriptie via OpenAI Whisper API
- 🔒 **Privacy optie** - Kies tussen cloud (snel) of lokaal (privé)
- 💰 **Budget tracking** - Automatische kostenbewaking
- 🚀 **Altijd aan** - Draait op de achtergrond via Launch Agent
- 📝 **Tech-aware** - Herkent Python, JavaScript, VS Code, GitHub, etc.

## 🚀 Snelle Start

### 1. Installeer Karabiner-Elements (voor fn toets)

```bash
brew install --cask karabiner-elements
```

Configureer fn → F18 mapping:
```bash
cp karabiner-fn-to-f18.json ~/.config/karabiner/assets/complex_modifications/
```

Open Karabiner-Elements → Complex Modifications → Add rule → Activeer "Map fn key to F18"

### 2. Installeer Python dependencies

```bash
git clone https://github.com/JOUW_USERNAME/typtalk.git
cd typtalk
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configureer API key

```bash
cp config.example.py config.py
```

Vul je OpenAI API key in in `config.py`:
```python
OPENAI_API_KEY = "sk-proj-..."
```

### 4. Start TypTalk

```bash
python typtalk.py
```

Houd fn ingedrukt, spreek, laat los → tekst wordt getypt! 🎉

## 🔧 Auto-start bij login

```bash
# Installeer Launch Agent
launchctl load ~/Library/LaunchAgents/com.typtalk.plist
```

TypTalk start nu automatisch bij inloggen en draait altijd op de achtergrond.

## ⚙️ Configuratie

Pas `config.py` aan:

```python
# Hotkey (vereist Karabiner voor fn)
HOTKEY = "f18"      # fn toets (aanbevolen)
# HOTKEY = "alt_r"  # of rechter Option toets

# Whisper mode
OPENAI_WHISPER_ENABLED = True   # Snel (OpenAI API)
# OPENAI_WHISPER_ENABLED = False  # Lokaal (gratis maar langzamer)

# Budget limieten
BUDGET_WARNING = 10.0  # Waarschuwing bij €10
BUDGET_LIMIT = 20.0    # Stop bij €20
```

## 💰 Kosten

**OpenAI Whisper API:** ~€0.006 per minuut audio
- 100 opnames/dag @ 10 sec = ~€3/maand
- Budget alerts bij €10 en €20

**Lokaal Whisper:** Gratis maar langzamer (~5-10s per opname)

## 🛠️ Probleemoplossing

### fn toets werkt niet
1. Check of Karabiner-Elements draait
2. Verificeer F18 mapping: Open Karabiner → Complex Modifications
3. Test met `python test_fn_key.py` (moet "F18 DETECTED!" tonen)

### Hotkey werkt niet
1. Check Accessibility permissions: Systeemvoorkeuren → Privacy → Accessibility
2. Voeg Python.app toe aan de lijst
3. Herstart TypTalk

### Geen audio
1. Check microphone permissions
2. Test microfoon in andere app

### Logs bekijken
```bash
tail -f /tmp/typtalk.log
```

## 📁 Bestanden

```
typtalk/
├── typtalk.py                    # Main app
├── config.py                     # Je persoonlijke config (niet in git)
├── config.example.py             # Template config
├── start_typtalk.sh              # Launch Agent starter
├── karabiner-fn-to-f18.json      # Karabiner config
├── test_fn_key.py                # Test fn toets detectie
└── requirements.txt              # Python dependencies
```

## 🎯 Tech Stack

- **Python 3.14**
- **OpenAI Whisper API** (of lokaal Whisper model)
- **Karabiner-Elements** (fn toets mapping)
- **pynput** (keyboard events & typing)
- **sounddevice** (audio recording)

## 📝 License

MIT

## 🙏 Credits

Gebouwd met [Claude Code](https://claude.com/claude-code)
