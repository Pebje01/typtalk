# TypTalk - Projectplan

## Visie
Een **privacy-first spraak-naar-tekst tool** voor macOS die altijd op de achtergrond draait en werkt met een simpele hotkey (fn of rechter Option). Net zo makkelijk als Wispr Flow maar dan sneller, goedkoper en met lokale verwerking optie.

---

## Must-Have Features (MVP)

### 1. Altijd Aan
- [x] Draait automatisch bij opstarten macOS
- [ ] Icoon in menubar (🎤) om status te zien
- [ ] Start automatisch zonder dat gebruiker iets hoeft te doen
- [ ] Crash recovery: herstart automatisch bij crash

**Implementatie:**
- macOS Launch Agent (`~/Library/LaunchAgents/com.typtalk.plist`)
- Menubar app met rumps of native Swift

---

### 2. Hotkey (Prioriteit!)
- [ ] **Primair: fn toets** (zoals Wispr Flow)
- [ ] **Fallback: rechter Option toets** (alt_r)
- [ ] Werkt systeem-breed (in ALLE apps)
- [ ] Hold-to-record: ingedrukt = opnemen, loslaten = stop & verwerk

**Technische uitdaging:**
- fn toets is moeilijk te detecteren op macOS
- Oplossing: Karabiner-Elements om fn → F18 te mappen
- Alternatief: Native Swift app met Carbon Event API

**Status nu:**
- ❌ Hotkey detectie werkt niet (pynput geblokkeerd door macOS)
- ✅ Manual Enter-versie werkt wel

**Volgende stappen:**
1. Test Karabiner-Elements voor fn → F18 mapping
2. Alternatief: Rebuild hotkey listener in Swift (Carbon API)
3. Zorg voor Input Monitoring permissions tijdens installatie

---

### 3. Snelheid ⚡
**Doel:** Transcriptie in <2 seconden voor 10 seconden spraak

**BESLISSING: OpenAI Whisper API VERPLICHT** ✅
- Beste balans tussen accuracy en snelheid
- Lokale Whisper is NIET een optie voor deze app
- Focus 100% op OpenAI API optimalisatie

**Waarom OpenAI Whisper API:**
| Aspect | Score |
|--------|-------|
| Snelheid | ⚡⚡⚡ 1-2 seconden |
| Accuracy | ⭐⭐⭐⭐⭐ 95%+ |
| Tech terms | ⭐⭐⭐⭐ Goed met prompting |
| Kosten | €3-5/maand bij normaal gebruik |

**Budget Alerts (AL INGESTELD):**
- ✅ Waarschuwing bij €10/maand
- ✅ **App gaat OP SLOT bij €20/maand** - geen transcripties meer tot nieuwe maand
- ✅ Kosten worden bijgehouden in `~/.typtalk_costs.json`
- ✅ Popup notificatie bij beide limieten

**Performance optimalisatie:**
- [ ] Whisper model pre-loaden bij app start
- [ ] Audio compressie voor snellere upload (bij API)
- [ ] Streaming transcriptie (typt al tijdens transcriptie)

---

### 4. Taalherkenning: Nederlands + Tech Terms

**Probleem:**
Whisper kent Nederlandse grammatica maar mist tech jargon zoals:
- "Claude Code" → vaak "Cloud Code"
- "GitHub" → "git hub"
- "OpenAI" → "open ai"
- "VS Code" → "vs code" (moet hoofdletters)

**Oplossing: Custom Vocabulary List**

```python
TECH_VOCABULARY = {
    # AI Tools
    "Claude": "Claude",
    "Claude Code": "Claude Code",
    "ChatGPT": "ChatGPT",
    "Gemini": "Gemini",
    "OpenAI": "OpenAI",
    "Anthropic": "Anthropic",
    "Midjourney": "Midjourney",
    "Stable Diffusion": "Stable Diffusion",

    # Dev Tools
    "GitHub": "GitHub",
    "VS Code": "VS Code",
    "Visual Studio": "Visual Studio",
    "Cursor": "Cursor",
    "PyCharm": "PyCharm",
    "Xcode": "Xcode",

    # Programming
    "Python": "Python",
    "JavaScript": "JavaScript",
    "TypeScript": "TypeScript",
    "React": "React",
    "Next.js": "Next.js",
    "Node.js": "Node.js",
    "MongoDB": "MongoDB",
    "PostgreSQL": "PostgreSQL",

    # Adobe Suite
    "Photoshop": "Photoshop",
    "Illustrator": "Illustrator",
    "After Effects": "After Effects",
    "Premiere Pro": "Premiere Pro",
    "Lightroom": "Lightroom",

    # Apple
    "macOS": "macOS",
    "iOS": "iOS",
    "Xcode": "Xcode",
    "Swift": "Swift",
    "Objective-C": "Objective-C",

    # Google
    "Google Cloud": "Google Cloud",
    "Firebase": "Firebase",
    "TensorFlow": "TensorFlow",

    # Diversen
    "API": "API",
    "SDK": "SDK",
    "CLI": "CLI",
    "GUI": "GUI",
    "URL": "URL",
    "JSON": "JSON",
    "YAML": "YAML",
    "Docker": "Docker",
    "Kubernetes": "Kubernetes",
}
```

**Implementatie:**
1. **Whisper prompt tuning:**
   ```python
   WHISPER_PROMPT = """Nederlands. Claude, Claude Code, GitHub, VS Code,
   ChatGPT, OpenAI, Gemini, Python, JavaScript, TypeScript, React, Photoshop,
   Illustrator, macOS, iOS, Docker, API, JSON..."""
   ```

2. **Post-processing correctie:**
   ```python
   def fix_tech_terms(text: str) -> str:
       for wrong, correct in TECH_VOCABULARY.items():
           # Case-insensitive replace
           text = re.sub(
               re.escape(wrong),
               correct,
               text,
               flags=re.IGNORECASE
           )
       return text
   ```

3. **Ollama/Gemini verbetering** (optioneel):
   - Stuur tekst naar Ollama met context: "Fix tech terms en Nederlandse grammatica"
   - Trade-off: +1-2 seconden, maar betere kwaliteit

**Taken:**
- [ ] Maak volledige tech vocabulary lijst (100+ termen)
- [ ] Implement post-processing
- [ ] Test met verschillende uitspraak variaties
- [ ] Maak custom vocabulary aanpasbaar door gebruiker

---

### 5. Werkt Overal
- [x] Werkt in Notes ✅
- [x] Werkt in TextEdit ✅
- [ ] Werkt in Browser (Chrome, Safari, Firefox)
- [ ] Werkt in VS Code / Cursor
- [ ] Werkt in Slack, Discord, WhatsApp
- [ ] Werkt in Mail app
- [ ] Werkt in Terminal

**Huidige implementatie:**
```python
from pynput.keyboard import Controller
keyboard_controller.type(text)  # Werkt in ALLE apps
```

**Potentiële problemen:**
- Sommige apps (Terminal) hebben special character handling
- Emoji's kunnen problemen geven
- Snelheid van typen (nu character-by-character)

**Optimalisaties:**
- [ ] Clipboard paste voor sneller (nadeel: overschrijft clipboard)
- [ ] Detect app en pas typing speed aan
- [ ] Special handling voor Terminal, VS Code

---

### 6. Continuous Recording Door Apps Heen
✅ **Dit werkt al!**

Huidige implementatie:
- Hotkey hold = start recording
- Hotkey release = stop recording
- Werkt onafhankelijk van welke app focus heeft

**Geen wijzigingen nodig**, mits hotkey detection werkt.

---

## Nice-to-Have Features

### 7. UI/UX Verbeteringen
- [ ] Visuele feedback tijdens opname (menubar icoon verandert)
- [ ] Progress indicator tijdens transcriptie
- [ ] Geluidje bij start/stop opname (optioneel)
- [ ] Toast notificatie met getranscribeerde tekst (voor review)
- [ ] Settings window:
  - [ ] Hotkey aanpassen
  - [ ] Whisper model kiezen (API vs lokaal)
  - [ ] Custom vocabulary toevoegen
  - [ ] Kosten overzicht (bij API gebruik)

### 8. Slimme Features
- [ ] Automatische punctuatie (punt, komma, vraagteken)
- [ ] Automatische capitalisatie (begin zin = hoofdletter)
- [ ] Commando's: "nieuwe regel" → Enter, "nieuwe paragraaf" → 2x Enter
- [ ] "verwijder dat" → verwijder laatste zin
- [ ] Multi-language support (auto-detect Nederlands vs Engels)

### 9. Privacy & Kosten
- [x] Lokale usage tracking (aantal transcripties, kosten) ✅
- [x] Budget limiet: €10 waarschuwing, €20 LOCK ✅
- [ ] OpenAI API key veilig opslaan (niet in config.py!)
- [ ] Audit log: welke audio is verstuurd naar API
- [ ] Kosten dashboard in settings UI

**BELANGRIJK: API Key Beveiliging**
- ❌ **NU:** API key staat in `config.py` (onveilig!)
- ✅ **MOET:** API key in macOS Keychain
- ✅ **OF:** Gebruiker voert eigen key in via settings
- [ ] Verwijder hardcoded keys uit repo voor productie

---

## Technische Architectuur

### Huidige Stack
```
TypTalk
├── Frontend: Python met rumps (menubar)
├── Hotkey: pynput (PROBLEEM: werkt niet)
├── Audio: sounddevice
├── Transcriptie: OpenAI Whisper API
└── Typing: pynput keyboard
```

### Voorgestelde Stack
```
TypTalk
├── Frontend: Swift menubar app
├── Hotkey: Swift Carbon Events API (of Karabiner helper)
├── Audio: AVFoundation (Swift) of sounddevice (Python)
├── Transcriptie: OpenAI Whisper API + lokaal Whisper fallback
├── Post-processing: Custom vocabulary replacer
└── Typing: Swift CGEvent (of pynput)
```

**Waarom Swift?**
- ✅ Native macOS permissions handling
- ✅ Betrouwbare hotkey detection
- ✅ Beter voor menubar apps
- ✅ Sneller voor audio handling
- ❌ Moeilijker voor Whisper (moet Python subprocess)

**Hybrid aanpak:**
- Swift frontend (menubar, hotkey, audio)
- Python backend (Whisper, text processing)
- IPC via stdin/stdout of sockets

---

## Development Roadmap

### Fase 1: Maak Hotkey Werkend (Week 1)
**Prioriteit: HOOG**

- [ ] **Optie A: Karabiner-Elements**
  - Install Karabiner-Elements
  - Map fn → F18
  - Update config.py: `HOTKEY = "f18"`
  - Test met pynput

- [ ] **Optie B: Swift Hotkey Listener**
  - Maak Swift CLI tool voor hotkey detection
  - Gebruik Carbon Events API
  - Pipe events naar Python script

- [ ] **Optie C: Rebuild in Swift**
  - Complete Swift app
  - Python als subprocess voor Whisper

**Deliverable:** Werkende hold-to-record hotkey

---

### Fase 2: Custom Vocabulary (Week 2)
- [ ] Maak comprehensive tech terms lijst (200+ woorden)
- [ ] Implement post-processing
- [ ] Test met real-world gebruik
- [ ] Maak aanpasbaar via settings UI

**Deliverable:** 95%+ accuracy voor tech terms

---

### Fase 3: Snelheidsoptimalisatie (Week 3)
- [ ] Benchmark huidige snelheid
- [ ] Test OpenAI API vs lokaal Whisper
- [ ] Implement model pre-loading
- [ ] Optimize audio encoding
- [ ] Target: <2s transcriptie voor 10s spraak

**Deliverable:** Sub-2-second transcriptie

---

### Fase 4: Auto-start & Launch Agent (Week 4)
- [ ] Maak Launch Agent plist
- [ ] Installer script die alles setup
- [ ] Menubar icoon met status
- [ ] Crash recovery

**Deliverable:** Werkt altijd op achtergrond

---

### Fase 5: Polish & Settings UI (Week 5-6)
- [ ] Settings window (Swift)
- [ ] Custom vocabulary editor
- [ ] Usage tracking & kosten dashboard
- [ ] Visuele feedback improvements

**Deliverable:** Production-ready app

---

## Installatie Flow (Toekomstige Gebruiker)

```
1. Download TypTalk.dmg
2. Sleep naar Applications
3. Open TypTalk
4. macOS vraagt permissions:
   ✓ Microfoon toegang
   ✓ Accessibility toegang
   ✓ Input Monitoring toegang
5. [Optioneel] Install Karabiner voor fn key
6. Klaar! fn ingedrukt houden = opnemen
```

**Install automation:**
- DMG met installer script
- Auto-detect of Karabiner nodig is
- Auto-add permissions (via TCC helper)
- Setup Launch Agent

---

## Kosten & Pricing

### Development Kosten
- Apple Developer Account: $99/jaar (voor code signing)
- OpenAI API credits: ~$5/maand tijdens dev
- **Totaal:** ~$150/jaar

### Operationele Kosten (Per Gebruiker)
**Scenario: 100 transcripties/dag @ 10 sec gemiddeld**
- Audio tijd: 1000 sec/dag = 16.6 min/dag
- OpenAI kosten: $0.006/min × 16.6 = $0.10/dag
- **Maandelijks: ~$3/gebruiker**

### Pricing Opties

**Optie 1: Freemium**
- Gratis: 50 transcripties/maand, lokaal Whisper only
- Pro ($10/maand): Unlimited, OpenAI API, custom vocabulary

**Optie 2: One-time Purchase**
- $30 one-time
- Lokaal Whisper included
- OpenAI API = BYOK (Bring Your Own Key)

**Optie 3: Open Source + Cloud Service**
- App is gratis & open source
- Cloud service: $5/maand voor OpenAI API

**Aanbeveling:** Optie 2 (one-time $30) met BYOK optie

---

## Huidige Status

### ✅ Wat Werkt
- Audio opname ✅
- OpenAI Whisper transcriptie ✅
- Lokaal Whisper (slow maar werkt) ✅
- Auto-typing in alle apps ✅
- Basic config systeem ✅

### ❌ Wat Niet Werkt
- Hotkey detection ❌ (BLOCKER!)
- Auto-start bij boot ❌
- Menubar icoon ❌
- Custom vocabulary ❌
- Performance (te langzaam) ❌

### 🚧 In Progress
- Projectplan (dit document!) 🚧
- Testing verschillende hotkey methodes 🚧

---

## Volgende Acties

### Deze Week (Prioriteit!)
1. **Fix hotkey detection** - Test Karabiner + F18 mapping
2. **Custom vocabulary** - Maak eerste lijst met 50 tech terms
3. **Speed test** - Benchmark OpenAI vs lokaal Whisper

### Next Sprint
4. **Launch Agent** - Auto-start implementeren
5. **Menubar app** - Swift of rumps
6. **Settings UI** - Basic settings window

---

## Competitie Analyse

### Wispr Flow
- **Prijs:** $60/jaar
- **Features:** fn hotkey, cloud-based, snel
- **Nadelen:** Duur, geen privacy optie, closed source

### TypTalk USP
- ✅ Goedkoper ($30 one-time vs $60/jaar)
- ✅ Privacy optie (lokaal Whisper)
- ✅ Custom vocabulary voor tech terms
- ✅ Open source mogelijk
- ✅ Nederlandse + Engelse tech taal

---

## Risico's & Mitigaties

| Risico | Impact | Mitigatie |
|--------|--------|-----------|
| Hotkey werkt niet | 🔴 HOOG | Karabiner, Swift rebuild, of fallback UI |
| macOS permissions complex | 🟡 MEDIUM | Goede installer, duidelijke docs |
| Whisper API kosten hoog | 🟡 MEDIUM | Lokale optie, BYOK model |
| Competitie (Wispr) | 🟢 LAAG | Focus op USP: privacy, custom vocab |

---

## Success Metrics

### Week 1
- [ ] Hotkey werkt 100% betrouwbaar
- [ ] <3s transcriptie voor 10s spraak

### Week 4
- [ ] Auto-start werkt
- [ ] 90%+ accuracy voor tech terms

### Week 8 (MVP Launch)
- [ ] 10 beta testers gebruiken dagelijks
- [ ] <2s transcriptie gemiddeld
- [ ] 95%+ tech term accuracy
- [ ] 0 crashes per dag

---

## Conclusie

**TypTalk heeft potentie om beter te zijn dan Wispr Flow** door:
1. Privacy-first (lokale optie)
2. Custom vocabulary voor tech jargon
3. Goedkoper pricing model
4. Open/transparant development

**Grootste uitdaging:** Hotkey detection werkend krijgen op macOS.

**Next step:** Test Karabiner-Elements voor fn key mapping deze week.

---

**Laatste update:** 3 feb 2025
**Versie:** 0.2-alpha
**Status:** In development
