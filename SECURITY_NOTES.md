# Security & API Key Notes

## ⚠️ BELANGRIJK: Voor Productie

### API Keys NIET in code!

**Huidige situatie (ONVEILIG):**
```python
# In config.py - NIET DOEN IN PRODUCTIE!
OPENAI_API_KEY = "sk-proj-k-3ZTmU5zNDh..."  # ❌ Hardcoded
GEMINI_API_KEY = "AIzaSyBKppH7KYW..."      # ❌ Hardcoded
```

**Voor productie (VEILIG):**

### Optie 1: macOS Keychain (Aanbevolen)
```python
import keyring

# Opslaan (1x tijdens setup)
keyring.set_password("TypTalk", "openai_api_key", user_api_key)

# Ophalen
OPENAI_API_KEY = keyring.get_password("TypTalk", "openai_api_key")
```

### Optie 2: Environment Variables
```python
import os
OPENAI_API_KEY = os.getenv("TYPTALK_OPENAI_KEY")
```

### Optie 3: User Settings UI
- Gebruiker voert eigen API key in via settings window
- Key wordt opgeslagen in Keychain
- BYOK (Bring Your Own Key) model

---

## Budget Limieten

**AL GECONFIGUREERD:**

```python
# In config.py
BUDGET_WARNING = 10.0   # Waarschuwing popup bij €10
BUDGET_LIMIT = 20.0     # APP LOCK bij €20
COST_FILE = "~/.typtalk_costs.json"
```

**Hoe het werkt:**
1. Bij €10: Popup waarschuwing "Je hebt €10 gebruikt deze maand"
2. Bij €20: **App gaat op slot** - geen transcripties meer
3. Reset automatisch bij nieuwe maand
4. Kosten tracking in JSON file

**Code implementatie (in wispr.py):**
```python
def _check_budget(self) -> bool:
    if self.monthly_cost >= config.BUDGET_LIMIT:
        self._notify("TypTalk - Budget Op!",
                     f"€{self.monthly_cost:.2f} bereikt. Gestopt.")
        return False

    if self.monthly_cost >= config.BUDGET_WARNING and not self.budget_warning_shown:
        self._notify("TypTalk - Budget Waarschuwing",
                     f"€{self.monthly_cost:.2f} van €{config.BUDGET_LIMIT} gebruikt.")
        self.budget_warning_shown = True

    return True
```

---

## Voor Git Repository

### .gitignore toevoegen:
```
# API Keys (NEVER commit!)
config.py
.env
*.key

# Cost tracking
.typtalk_costs.json

# User settings
.typtalk_settings.json
```

### config.example.py maken:
```python
"""
Voorbeeld configuratie - kopieer naar config.py
"""

# OpenAI API
OPENAI_API_KEY = "sk-proj-YOUR_KEY_HERE"  # Haal bij platform.openai.com

# Budget limieten
BUDGET_WARNING = 10.0  # Waarschuwing in euro
BUDGET_LIMIT = 20.0    # App lock in euro
```

---

## Checklist voor Productie

- [ ] Verwijder hardcoded API keys uit config.py
- [ ] Voeg config.py toe aan .gitignore
- [ ] Maak config.example.py met placeholders
- [ ] Implement Keychain storage voor API keys
- [ ] Settings UI voor gebruiker om key in te voeren
- [ ] Test budget alerts (€10 en €20)
- [ ] Documenteer in README hoe gebruikers API key instellen

---

## API Kosten Tracking

**Huidige implementatie:**
- Kosten worden opgeslagen in `~/.typtalk_costs.json`
- Format:
  ```json
  {
    "month": "2025-02",
    "total_cost": 3.45,
    "transcriptions": 127
  }
  ```
- Reset automatisch bij nieuwe maand

**Verbetering mogelijk:**
- Dashboard in settings UI
- Grafiek van kosten per dag
- Schatting: "Bij dit tempo: €X deze maand"

---

**Laatste update:** 3 feb 2025
