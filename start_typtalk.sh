#!/bin/bash
# TypTalk Startup Script

cd "$(dirname "$0")"

# Stop oude daemon als die vast zit
pkill -f typtalk_daemon 2>/dev/null

# Verwijder oude pipe
rm -f ~/.typtalk_control

# Wacht even
sleep 1

# Start daemon
echo "🚀 TypTalk daemon starten..."
./venv/bin/python3 typtalk.py > typtalk.log 2>&1 &

# Wacht en check
sleep 3

if pgrep -f "typtalk.py" > /dev/null; then
    echo "✅ TypTalk daemon gestart!"
    echo ""
    echo "Fn-toets dictee is actief 🎤"
else
    echo "❌ Fout bij starten"
    cat typtalk_daemon.log
    exit 1
fi
