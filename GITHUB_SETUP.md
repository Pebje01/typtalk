# GitHub Repo Setup

## Optie 1: Via GitHub CLI (aanbevolen)

```bash
# Login (eenmalig)
gh auth login

# Maak repo aan
gh repo create typtalk --public --source=. --remote=origin --push

# Klaar!
```

## Optie 2: Via GitHub website

1. Ga naar https://github.com/new
2. Repository naam: `typtalk`
3. Description: "Privacy-first voice-to-text for macOS with fn key hotkey"
4. Public/Private: Kies zelf
5. Klik "Create repository"

Dan in terminal:

```bash
git remote add origin https://github.com/JOUW_USERNAME/typtalk.git
git branch -M main
git push -u origin main
```

## Huidige status

✅ Code is committed
✅ API keys zijn NIET in de repo (veilig!)
✅ config.example.py is gemaakt voor anderen

Klaar om te pushen!
