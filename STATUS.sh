#!/bin/bash
# Check TypTalk status

if pgrep -f "typtalk_daemon.py" > /dev/null; then
    echo "✅ TypTalk daemon draait"
    echo ""
    echo "Laatste activiteit:"
    tail -5 ~/typtalk/typtalk_daemon.log
else
    echo "❌ TypTalk daemon draait NIET"
    echo ""
    echo "Herstart met: ./START_TYPTALK.sh"
fi
