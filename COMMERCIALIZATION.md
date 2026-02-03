# TypTalk Commercialisatie Plan

## Wat moet veranderen voor betaalde versie

### 1. Licentie & Verwijzingen (BELANGRIJK)

**Te verwijderen:**
- [ ] Alle API keys uit `config.py` (NEVER commit deze!)
- [ ] Hardcoded credentials
- [ ] Debug logs met gevoelige info

**Te veranderen:**
- [ ] LICENSE file (nu open source?) → Proprietary license
- [ ] Copyright notices in alle bestanden
- [ ] "Gebouwd met Claude Code" → eigenaar credits

### 2. License Management Systeem

**Opties:**

#### Optie A: Gumroad (Makkelijkst)
```python
# license_manager.py
import requests

def verify_license(license_key: str) -> bool:
    """Verify license via Gumroad API"""
    response = requests.post(
        "https://api.gumroad.com/v2/licenses/verify",
        data={
            "product_id": "JOUW_PRODUCT_ID",
            "license_key": license_key
        }
    )
    return response.json()["success"]

# In typtalk.py bij startup
if not verify_license(user_license_key):
    show_activation_window()
    exit()
```

**Gumroad voordelen:**
- Geen eigen payment processing
- Automatische licentie generatie
- Email delivery
- $10 flat fee per maand
- 10% + payment fees

#### Optie B: Paddle (Professioneler)
- Merchant of record (zij handelen VAT/tax)
- Betere analytics
- Subscription management
- 5% + payment processing

#### Optie C: Custom (Meeste controle)
- Stripe voor payments
- Eigen licentie database
- Meeste werk maar meeste flexibiliteit

### 3. App Structuur Aanpassingen

**Info.plist updates:**
```xml
<!-- Voeg toe aan TypTalk.app/Contents/Info.plist -->
<key>NSHumanReadableCopyright</key>
<string>Copyright © 2026 Jouw Naam. All rights reserved.</string>

<key>CFBundleVersion</key>
<string>1.0.0</string>

<key>LSApplicationCategoryType</key>
<string>public.app-category.productivity</string>
```

**Activation window toevoegen:**
```python
# activation.py
import tkinter as tk
from tkinter import messagebox

class ActivationWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("TypTalk Activeren")

        tk.Label(self.window, text="Voer je licentie code in:").pack()
        self.license_entry = tk.Entry(self.window, width=40)
        self.license_entry.pack()

        tk.Button(
            self.window,
            text="Activeren",
            command=self.activate
        ).pack()

        tk.Button(
            self.window,
            text="Koop Licentie",
            command=self.open_store
        ).pack()

    def activate(self):
        license_key = self.license_entry.get()
        if verify_license(license_key):
            save_license(license_key)
            messagebox.showinfo("Succes", "TypTalk geactiveerd!")
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Ongeldige licentie")

    def open_store(self):
        import webbrowser
        webbrowser.open("https://jouwwebsite.com/buy")
```

### 4. Pricing Models

#### Model 1: One-time Purchase ($20-40)
**Voordelen:**
- Simpel voor gebruikers
- Geen recurring billing complexiteit
- Hogere conversie

**Nadelen:**
- Geen recurring revenue
- Moeilijk updates te financieren

**Implementatie:**
```python
# Eenmalige activatie check
def check_license():
    license_file = Path.home() / ".typtalk_license"
    if not license_file.exists():
        return False

    license_data = json.loads(license_file.read_text())
    return verify_license(license_data["key"])
```

#### Model 2: Subscription ($5-10/maand)
**Voordelen:**
- Recurring revenue
- Funding voor updates
- Lagere entry price

**Nadelen:**
- Meer complexiteit (payment processing, cancellations)
- Subscription fatigue

**Implementatie:**
```python
# Check subscription status
def check_subscription():
    response = requests.get(
        f"https://api.paddle.com/subscription/{user_id}/status"
    )
    return response.json()["state"] == "active"
```

#### Model 3: Freemium
**Free tier:**
- 100 transcripties per maand
- Basis features
- Lokale Whisper only

**Pro tier ($10/maand):**
- Unlimited transcripties
- Cloud Whisper API (sneller)
- Custom vocabulary
- Priority support

**Implementatie:**
```python
class UsageTracker:
    def __init__(self):
        self.usage_file = Path.home() / ".typtalk_usage.json"
        self.usage = self._load_usage()

    def can_transcribe(self) -> bool:
        if self.is_pro_user():
            return True

        # Free tier: 100/maand
        return self.usage["monthly_count"] < 100

    def record_usage(self):
        self.usage["monthly_count"] += 1
        self._save_usage()
```

### 5. API Keys Management (KRITIEK)

**NOOIT in code:**
```python
# FOUT - hardcoded API keys
OPENAI_API_KEY = "sk-proj-..."
GEMINI_API_KEY = "AIza..."
```

**WEL zo:**
```python
# config.py
OPENAI_API_KEY = os.getenv("TYPTALK_OPENAI_KEY")
GEMINI_API_KEY = os.getenv("TYPTALK_GEMINI_KEY")

# Of via keychain op macOS
import keyring
OPENAI_API_KEY = keyring.get_password("typtalk", "openai_key")
```

**Voor gebruikers met eigen keys:**
```python
# Settings window
def save_api_keys():
    user_openai_key = settings_window.openai_entry.get()
    if user_openai_key:
        keyring.set_password("typtalk", "openai_key", user_openai_key)
```

### 6. Analytics & Crash Reporting

**Optie 1: Sentry (Crashes)**
```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://...@sentry.io/...",
    traces_sample_rate=1.0
)
```

**Optie 2: Mixpanel (Usage Analytics)**
```python
from mixpanel import Mixpanel

mp = Mixpanel("YOUR_TOKEN")

mp.track(user_id, "Transcription Started")
mp.track(user_id, "Transcription Completed", {
    "duration_seconds": 5,
    "word_count": 50
})
```

### 7. Auto-Update Systeem

**Sparkle framework (macOS standaard):**
```xml
<!-- Info.plist -->
<key>SUFeedURL</key>
<string>https://jouwwebsite.com/appcast.xml</string>
<key>SUPublicEDKey</key>
<string>JOUW_PUBLIC_KEY</string>
```

**appcast.xml voorbeeld:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>TypTalk Updates</title>
    <item>
      <title>Version 1.1.0</title>
      <pubDate>Mon, 03 Feb 2026 12:00:00 +0000</pubDate>
      <enclosure
        url="https://jouwwebsite.com/TypTalk-1.1.0.dmg"
        sparkle:version="1.1.0"
        type="application/octet-stream"
      />
    </item>
  </channel>
</rss>
```

### 8. Website & Marketing

**Minimale website nodig:**
- Landing page met demo video
- Pricing page
- Download/Buy button
- Support/FAQ
- Privacy policy
- Terms of service

**Hosting opties:**
- Vercel/Netlify (gratis voor static)
- Webflow (no-code, $15/maand)

**Marketing kanalen:**
- Product Hunt launch
- Hacker News Show HN
- Reddit (r/macapps, r/productivity)
- Twitter/X
- Mac app review sites

### 9. Support Systeem

**Opties:**
- Email support (eenvoudigst)
- Intercom ($39/maand)
- Discord community (gratis)
- Help Scout ($20/maand)

### 10. Legal Requirements

**Nodig:**
- Privacy Policy (GDPR compliant)
- Terms of Service
- Refund policy
- Business registratie (eenmanszaak/BV)
- BTW nummer (als je >€20k omzet verwacht)

### 11. Kosten Overzicht

**Eenmalige kosten:**
- Apple Developer Account: $99/jaar
- Domain naam: €10/jaar
- Logo/design: €100-500

**Maandelijkse kosten (minimaal):**
- Hosting: €0-10
- Payment processor: 5-10% + €0.30 per transactie
- Analytics/Sentry: €0-25

**Optionele kosten:**
- Support tool: €20-50/maand
- Email marketing: €10-30/maand
- Website builder: €15/maand

### 12. Development Roadmap

**Pre-launch (2-4 weken):**
- [ ] Licentie systeem implementeren
- [ ] Activation window bouwen
- [ ] API keys uit code halen
- [ ] Analytics toevoegen
- [ ] Code signing & notarisatie
- [ ] Website bouwen
- [ ] Beta testing met 10-20 users

**Launch (week 1):**
- [ ] Product Hunt
- [ ] Hacker News
- [ ] Social media
- [ ] Mac app sites contacten

**Post-launch (maandelijks):**
- [ ] Feature updates
- [ ] Bug fixes
- [ ] Customer feedback verwerken
- [ ] Marketing content

### 13. Price Points & Positioning

**Budget option ($20 one-time):**
- Target: Studenten, hobbyisten
- Expected sales: 50-100/maand
- Revenue: $1000-2000/maand

**Premium option ($40 one-time):**
- Target: Professionals, developers
- Expected sales: 20-50/maand
- Revenue: $800-2000/maand

**Pro subscription ($10/maand):**
- Target: Power users, businesses
- Expected: 50-100 subscribers
- Revenue: $500-1000/maand recurring

**Aanbeveling:** Start met $29 one-time, test de markt

### 14. Competition Analysis

**Versus commercial alternatives:**
- Talon Voice: $15/maand (gericht op coders, voice commands)
- Dragon: $150 one-time (Windows, corporate)
- macOS Dictation: Gratis (beperkter)

**TypTalk USP:**
- Privacy-first (lokale processing optie)
- Goedkoper dan concurrentie
- Native macOS
- Developer-friendly
- Nederlandse + Engelse taal

**Pricing strategy:**
- Premium dan Dictation (want beter)
- Goedkoper dan Talon (maar minder features)
- Veel goedkoper dan Dragon (maar Mac-only)

→ **Sweet spot: $25-35 one-time purchase**

## Aanbevolen Stappenplan

### Fase 1: Technical (2 weken)
1. API keys uit code halen
2. Gumroad licentie systeem implementeren
3. Activation window bouwen
4. Code signing + notarisatie
5. Beta test met 10 vrienden

### Fase 2: Business (1 week)
1. Website bouwen (Webflow/Carrd)
2. Gumroad product aanmaken
3. Privacy policy + ToS schrijven
4. Demo video maken

### Fase 3: Launch (week 1)
1. Product Hunt launch
2. Hacker News Show HN
3. Reddit posts
4. Twitter/X aankondiging

### Fase 4: Iterate (ongoing)
1. Customer feedback verzamelen
2. Features toevoegen
3. Marketing content maken
4. Community bouwen

## Quick Win: Beta Launch

**Nu al geld verdienen zonder alles af te hebben:**

1. "Beta licentie" verkopen op Gumroad ($19)
2. Simpele license check toevoegen (30 min werk)
3. Website met "Early Access" pitch
4. 50% korting voor early adopters
5. Feedback verzamelen voor v1.0

**Voordelen:**
- Validatie of mensen willen betalen
- Funding voor verdere development
- Beta testers die feedback geven
- Marketing testimonials

**Minimal viable payment:**
```python
# license_check.py
def is_valid_license():
    license_file = Path.home() / ".typtalk_license"
    if not license_file.exists():
        return False

    try:
        license_key = license_file.read_text().strip()
        # Simpele check: moet starten met "TYPTALK-"
        # Later vervangen door echte API check
        return license_key.startswith("TYPTALK-")
    except:
        return False

# typtalk.py
if not is_valid_license():
    print("TypTalk vereist een licentie.")
    print("Koop een licentie op: https://gumroad.com/l/typtalk")
    exit(1)
```

Dan verkoop je licentie codes zoals: `TYPTALK-XXXX-XXXX-XXXX`

**Deze aanpak laat je in 1 dag lanceren en valideren!**
