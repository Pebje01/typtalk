"""
Configuratie voor TypTalk - EXAMPLE FILE
Kopieer dit bestand naar config.py en vul je eigen API keys in
"""

# Hotkey configuratie
HOTKEY = "f18"  # fn toets (via Karabiner-Elements mapping)

# Alternatieve hotkeys:
# HOTKEY = "alt_r"   # Rechter Option toets
# HOTKEY = "ctrl_r"  # Rechter Control
# HOTKEY = "cmd_r"   # Rechter Command

# Whisper configuratie
WHISPER_MODEL = "small"  # Opties: tiny, base, small, medium, large
WHISPER_LANGUAGE = "nl"  # Nederlands
WHISPER_PROMPT = """Nederlands. TypTalk, Whisper, Gemini, API, Claude, OpenAI, Python, JavaScript, TypeScript, React, VS Code, GitHub, terminal, code, programmeren, software, developer, functie, variabele, database, server, frontend, backend."""

# Ollama configuratie
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "mistral"  # Beter voor grammatica correctie
OLLAMA_ENABLED = False  # Zet op True voor Ollama grammatica correctie

# Gemini configuratie (aanbevolen voor grammatica correctie)
GEMINI_ENABLED = False  # Uit voor snelheid, OpenAI Whisper is al goed genoeg
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Vul je eigen key in
GEMINI_MODEL = "gemini-2.0-flash"

# OpenAI configuratie (voor snellere Whisper)
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"  # Vul je eigen key in
OPENAI_WHISPER_ENABLED = True  # Gebruik cloud Whisper (sneller) ipv lokaal

# System prompt voor tekstverbetering
OLLAMA_SYSTEM = """Taak: Corrigeer de Nederlandse tekst.
Regels:
- Fix alleen spelling en grammatica
- Behoud alle woorden en betekenis
- Output ALLEEN de gecorrigeerde tekst
- GEEN uitleg, GEEN commentaar, GEEN aanhalingstekens"""

# Audio configuratie
SAMPLE_RATE = 16000  # Whisper verwacht 16kHz
CHANNELS = 1  # Mono

# Typing configuratie
TYPING_DELAY = 0.01  # Seconden tussen karakters (0 voor maximale snelheid)

# Rate limiting (veiligheid)
MAX_REQUESTS_PER_MINUTE = 10  # Maximum API calls per minuut
REQUEST_COOLDOWN = 2  # Minimum seconden tussen requests

# Budget limieten (in euro's)
BUDGET_WARNING = 10.0  # Waarschuwing bij dit bedrag
BUDGET_LIMIT = 20.0  # Stop bij dit bedrag
COST_FILE = "~/.typtalk_costs.json"  # Bestand om kosten bij te houden

# Debug modus
DEBUG = True  # Print extra informatie naar console
