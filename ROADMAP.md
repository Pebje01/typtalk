# TypTalk Roadmap & Verbeterpunten

## ✅ V1.0 - Werkende MVP (CURRENT)

- [x] fn toets hotkey detection via Karabiner
- [x] OpenAI Whisper API transcriptie
- [x] Budget tracking en limieten
- [x] Launch Agent voor auto-start
- [x] Werkt in alle apps
- [x] Auto-restart bij crash

## 🎯 V1.1 - Polish & UX (Week 1-2)

### High Priority
- [ ] **Menubar icoon** - Status indicator (🎤 idle, 🔴 recording, ⏳ processing)
- [ ] **Visual feedback** - Korte animatie/geluid bij start/stop opname
- [ ] **Settings UI** - Simpel window voor:
  - API key invoeren
  - Hotkey selecteren
  - Budget limieten instellen
  - Kosten overzicht
- [ ] **Error handling** - Betere foutmeldingen met actionable fixes
- [ ] **Installation script** - One-command installer

### Medium Priority
- [ ] **Custom vocabulary** - User-defined tech terms toevoegen
- [ ] **Multiple languages** - Auto-detect Nederlands/Engels
- [ ] **Keyboard shortcuts** - Cmd+Shift+R = reload, Cmd+Shift+P = pause/resume
- [ ] **Activity log** - Laatste 10 transcripties tonen

## 🚀 V2.0 - Advanced Features (Month 2-3)

### Smart Text Processing
- [ ] **Auto-punctuation** - "punt", "komma", "vraagteken" → . , ?
- [ ] **Voice commands** - "nieuwe regel", "verwijder dat", "undo"
- [ ] **Context awareness** - Verschillende modi voor chat/email/code
- [ ] **Text replacement** - Snelkoppelingen (bijv. "adres" → vol adres)

### Performance
- [ ] **Streaming transcription** - Begin typen tijdens transcriptie
- [ ] **Audio preprocessing** - Noise reduction, volume normalization
- [ ] **Caching** - Herbruik resultaten voor identieke audio
- [ ] **Batch mode** - Meerdere opnames achter elkaar

### Privacy & Security
- [ ] **Lokale Whisper optimalisatie** - GPU acceleration, model quantization
- [ ] **Keychain integratie** - API keys veilig opslaan in macOS Keychain
- [ ] **Audit mode** - Log alle API calls (voor compliance)
- [ ] **End-to-end encryption** - Voor wie het wil (paranoia mode)

## 📦 V3.0 - Distribution & Scale (Month 4+)

### Professionalisering
- [ ] **Mac App Store** - Signed & notarized .app bundle
- [ ] **Auto-update** - Via Sparkle framework
- [ ] **Crash reporting** - Sentry integratie
- [ ] **Analytics** - Anonymous usage stats (opt-in)

### Business Model
- [ ] **Freemium** - 50 transcriptions/maand gratis, Pro = unlimited
- [ ] **Team features** - Shared custom vocabulary, usage dashboard
- [ ] **API** - TypTalk als service voor andere apps

### Platform Expansion
- [ ] **Windows port** - Via Python + AutoHotkey
- [ ] **Linux support** - Voor developers
- [ ] **Mobile companion** - iOS app met sync

## 🐛 Known Issues & Fixes

### Bugs
- [ ] **Cost tracking bug** - Wordt nu aangeroepen met `duration` maar functie verwacht `audio_seconds`
- [ ] **Launch Agent permissions** - Soms start niet na reboot (permissions issue)
- [ ] **Multiple instances** - Geen check of TypTalk al draait

### Technical Debt
- [ ] **Config validation** - Check of API key valid is bij startup
- [ ] **Better logging** - Structured logging met levels (DEBUG, INFO, ERROR)
- [ ] **Unit tests** - Coverage voor core functies
- [ ] **CI/CD** - GitHub Actions voor auto-testing

## 💡 Feature Requests

Community ideas (add via GitHub Issues):
- [ ] Browser extension voor voice input in webapps
- [ ] Clipboard history met voice search
- [ ] Voice macros (custom workflows)
- [ ] Multi-user support (meerdere API keys)

## 🎨 Design Improvements

- [ ] Better app icon (nu placeholder)
- [ ] Notificatie design (native macOS style)
- [ ] Settings UI mockups
- [ ] Onboarding flow

## 📊 Metrics to Track

Success criteria:
- **Speed**: <1s transcriptie voor 10s audio (current: 0.8s ✅)
- **Accuracy**: >95% correct transcriptie (need to measure)
- **Reliability**: <1 crash per maand
- **Cost**: <€5/maand voor normal gebruik
- **User satisfaction**: NPS >50

## 🔧 Development Setup Improvements

- [ ] Docker setup voor consistent dev environment
- [ ] Pre-commit hooks voor code quality
- [ ] Automated releases via GitHub Actions
- [ ] Better dev documentation

## Notes

**Priority order:**
1. Fix critical bugs (cost tracking)
2. Menubar UI (v1.1)
3. Settings window (v1.1)
4. Voice commands (v2.0)
5. Distribution (v3.0)

**Timeline:**
- V1.1: 2 weken
- V2.0: 2 maanden
- V3.0: 4+ maanden

Laatste update: 3 feb 2025
