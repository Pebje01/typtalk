# Wispr Flow Clone

Een Python-tool die spraak opneemt via een hotkey, transcribeert met Whisper, verbetert met Ollama, en de tekst direct typt waar de cursor staat.

## Installatie

### 1. Python Dependencies

```bash
cd ~/wispr-clone
pip install -r requirements.txt
```

### 2. Ollama Installeren

```bash
# Installeer Ollama
brew install ollama

# Start Ollama service
ollama serve

# Download een model (in een nieuwe terminal)
ollama pull llama3.2
```

### 3. Karabiner-Elements (Optioneel, voor fn-toets)

Als je de fn-toets wilt gebruiken als hotkey:

```bash
# Installeer Karabiner-Elements
brew install --cask karabiner-elements
```

Na installatie:
1. Open Karabiner-Elements
2. Ga naar "Complex Modifications"
3. Klik "Add rule" → "Import more rules from the Internet"
4. Of kopieer `karabiner-fn-to-f18.json` naar `~/.config/karabiner/assets/complex_modifications/`
5. Activeer de "Map fn key to F18" regel

### 4. macOS Permissies

Het script heeft de volgende permissies nodig:
- **Accessibility**: Voor keyboard input/output (Systeemvoorkeuren → Privacy & Beveiliging → Accessibility)
- **Microphone**: Voor audio opname (wordt automatisch gevraagd)

## Gebruik

```bash
cd ~/wispr-clone
python wispr.py
```

1. Houd de hotkey ingedrukt (standaard: F18)
2. Spreek je tekst in
3. Laat de hotkey los
4. Wacht even terwijl de tekst wordt verwerkt
5. De verbeterde tekst wordt automatisch getypt waar je cursor staat

Druk `Ctrl+C` om te stoppen.

## Configuratie

Pas `config.py` aan voor je voorkeuren:

```python
# Hotkey opties
HOTKEY = "f18"      # Standaard (via Karabiner)
HOTKEY = "alt_r"    # Rechter Option toets
HOTKEY = "ctrl_r"   # Rechter Control toets

# Whisper model (groter = nauwkeuriger maar langzamer)
WHISPER_MODEL = "base"   # Snel
WHISPER_MODEL = "small"  # Nauwkeuriger

# Ollama model
OLLAMA_MODEL = "llama3.2"  # Standaard
OLLAMA_MODEL = "mistral"   # Alternatief
```

## Probleemoplossing

### "Ollama niet bereikbaar"
Zorg dat Ollama draait:
```bash
ollama serve
```

### Hotkey werkt niet
1. Check of je de juiste permissies hebt gegeven (Accessibility)
2. Probeer een andere hotkey in `config.py`
3. Als je F18 gebruikt, check of Karabiner correct is geconfigureerd

### Geen audio
1. Check microphone permissies
2. Test je microfoon in een andere app

### Trage verwerking
- Gebruik een kleiner Whisper model (`tiny` of `base`)
- Gebruik een sneller Ollama model
