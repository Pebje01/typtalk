#!/bin/bash
# TypTalk Watchdog - houdt daemon draaiend
# Deze checkt elke 10 seconden of daemon nog draait en herstart automatisch

cd "$(dirname "$0")"

echo "🐕 TypTalk Watchdog gestart - houdt daemon draaiend"

while true; do
    if ! pgrep -f "typtalk_daemon.py" > /dev/null; then
        echo "⚠️  $(date): Daemon gestopt, herstarten..."

        # Cleanup
        pkill -9 -f typtalk_daemon 2>/dev/null
        rm -f ~/.typtalk_control 2>/dev/null
        sleep 1

        # Herstart
        ./venv/bin/python3 typtalk_daemon.py > typtalk_daemon.log 2>&1 &

        sleep 3
        if pgrep -f "typtalk_daemon.py" > /dev/null; then
            echo "✅ $(date): Daemon herstart succesvol"
        else
            echo "❌ $(date): Herstart gefaald, probeer over 10 sec opnieuw"
        fi
    fi

    sleep 10
done
