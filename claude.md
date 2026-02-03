# TypTalk - Spraak-naar-tekst voor macOS

## Wat is het?

TypTalk is een macOS applicatie die spraak omzet naar tekst via een hotkey. Je houdt de rechter Option toets ingedrukt, spreekt je tekst in, en de tekst wordt automatisch getypt waar je cursor staat.

Voice-to-text met privacy-first design: alle processing kan lokaal draaien, of via OpenAI API wanneer gewenst.

## Hoe werkt het?

```
1. Gebruiker houdt hotkey ingedrukt (alt_r = rechter Option)
2. TypTalk neemt audio op via microfoon
3. Bij loslaten: audio wordt getranscribeerd met Whisper
4. Tekst wordt verbeterd met Ollama/Gemini (optioneel)
5. Tekst wordt automatisch getypt
```

## Tech Stack

- **Python 3.14** - Main language
- **pynput** - Keyboard event listening & typing
- **sounddevice** - Audio recording
- **Whisper** - Speech-to-text (local of OpenAI API)
- **Ollama/Gemini** - Text improvement (optioneel)
- **Swift** - App launcher voor macOS permissions

## Bestanden

```
typtalk/
├── typtalk.py              # Main application
├── config.py               # Configuratie (hotkey, models, etc)
├── launcher.swift          # Swift launcher voor macOS
├── TypTalk.app/            # macOS app bundle
│   └── Contents/
│       ├── Info.plist      # App metadata
│       └── MacOS/
│           └── TypTalk     # Compiled Swift launcher
├── requirements.txt        # Python dependencies
├── build_release.sh        # Build script voor distributie
└── install_for_users.sh    # User-friendly installer
```

## Configuratie

In `config.py`:

```python
# Hotkey
HOTKEY = "alt_r"  # Rechter Option toets

# Whisper
WHISPER_MODEL = "small"  # small, medium, large
USE_OPENAI_WHISPER = False  # True voor OpenAI API

# Text verbetering
IMPROVE_TEXT = True
USE_OLLAMA = True  # False voor Gemini
OLLAMA_MODEL = "llama3.2"

# Budget
MAX_DAILY_COST = 5.00  # Euro per dag
```

## macOS Permissies

TypTalk heeft 3 permissies nodig:

1. **Microfoon** - Voor audio opname
2. **Accessibility** - Voor keyboard monitoring
3. **Input Monitoring** - Voor hotkey detectie

Deze worden bij eerste start automatisch gevraagd.

## Development Setup

```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Run
python typtalk.py
```

## Permissies handmatig instellen

```bash
# Helper script
./add_to_accessibility.sh
```

Of handmatig:
1. Systeeminstellingen → Privacy & Beveiliging
2. Voeg toe aan Microfoon, Accessibility, Input Monitoring:
   - `/opt/homebrew/.../Python.app` (voor development)
   - `/Applications/TypTalk.app` (voor production)

## Build voor distributie

```bash
# Build standalone app met PyInstaller
./build_release.sh

# Installer voor gebruikers
./install_for_users.sh
```

## Roadmap naar productie

### Fase 1: MVP (nu)
- [x] Basis functionaliteit
- [x] Hotkey detection
- [x] Whisper transcriptie
- [x] Auto-typing
- [x] macOS app bundle
- [ ] Hotkey werkt reliable (current issue)

### Fase 2: Beta
- [ ] PyInstaller build met alle dependencies
- [ ] Code signing
- [ ] Notarisatie (vereist Apple Developer Account)
- [ ] .dmg installer
- [ ] User-friendly installer script

### Fase 3: Launch
- [ ] Mac App Store versie
- [ ] Website met downloads
- [ ] Betaalde versie met cloud features
- [ ] Teams/business features

### Fase 4: Growth
- [ ] Windows versie
- [ ] Cloud sync voor instellingen
- [ ] Custom vocabulary
- [ ] Multi-language support

## Current Issues

### Hotkey detection werkt niet (BLOCKER!)
**Status:** Debugging - 3 feb 2025

**Probleem:**
- pynput detecteert geen keyboard events ondanks alle permissions
- 2 dagen geleden werkte het WEL met rechter Option toets
- **fn toets werkt ook niet meer** (fn+backspace = delete werkt niet)
- "This process is not trusted" error ondanks permissions

**Permissions gegeven:**
- ✅ Python.app in Accessibility
- ✅ Python.app in Input Monitoring
- ✅ Terminal in Accessibility
- ✅ Terminal in Input Monitoring
- ✅ TypTalk.app in Accessibility

**Mogelijke oorzaken:**
1. macOS update heeft permissions gereset
2. **fn toets hardware probleem** (werkt nergens meer)
3. pynput compatibility issue met macOS versie
4. Permission changes vereisen macOS reboot

**Wat WEL werkt:**
- ✅ OpenAI Whisper API transcriptie (snel & accuraat)
- ✅ Auto-typing in alle apps
- ✅ Enter-based opname (typtalk_simple.py)

**Next steps:**
1. **Restart macOS** (permissions activeren)
2. Test rechter Option key na reboot
3. Als nog niet werkt: Karabiner-Elements voor F18 mapping
4. Laatste optie: Rebuild in Swift met native Carbon Events API

## Distributie opties

### Optie 1: Mac App Store
- **Pro:** Makkelijkste voor gebruikers, automatische updates
- **Con:** $99/jaar, 30% commissie, review proces

### Optie 2: Notarized .dmg
- **Pro:** Professioneel, gebruikers vertrouwen het
- **Con:** Apple Developer Account nodig

### Optie 3: Homebrew
- **Pro:** Makkelijk voor developers
- **Con:** Te technisch voor gewone gebruikers

### Optie 4: Electron/Tauri
- **Pro:** Cross-platform (Mac/Windows/Linux)
- **Con:** Grotere app size

**Aanbeveling:** Start met Optie 2 (notarized .dmg), later naar Mac App Store

## Kosten

### Development
- Python + libraries: Gratis
- Whisper (local): Gratis
- Ollama (local): Gratis

### Distributie
- Apple Developer Account: $99/jaar (optioneel maar aanbevolen)

### API kosten (optioneel)
- OpenAI Whisper API: ~$0.006 per minuut audio
- Gemini API: Gratis tier beschikbaar

## Business Model opties

1. **Freemium:**
   - Gratis: Basis features, lokale modellen
   - Betaald ($5-10/maand): Cloud sync, betere modellen, prioriteit support

2. **One-time purchase:**
   - $20-30 voor lifetime license
   - Updates included

3. **Open source + support:**
   - Gratis voor iedereen
   - Betaalde support voor bedrijven

## Vergelijkbare producten

- **Talon Voice:** $15/maand, gericht op developers
- **Dragon Naturally Speaking:** $150 one-time, Windows-only
- **macOS Dictation:** Gratis maar minder nauwkeurig

**TypTalk USP:**
- Lokale processing (privacy)
- Open source mogelijk
- macOS native
- Flexibel: keuze tussen lokale en cloud models

## Notes

- Gebouwd met hulp van Claude Code
- Privacy-first: alle processing kan lokaal
- Modular design: makkelijk om Whisper/Ollama te vervangen
- Geschikt voor Nederlandse én Engelse spraak
