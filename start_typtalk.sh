#!/bin/bash
# TypTalk starter script - draait altijd op de achtergrond

# Ga naar de juiste directory
cd /Users/daleyjansen_1/typtalk

# Activeer virtual environment
source venv/bin/activate

# Start TypTalk
exec python3 typtalk.py
