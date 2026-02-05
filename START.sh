#!/bin/bash
# TypTalk - Simpel start script
# Gebruik: ./START.sh

cd "$(dirname "$0")"

echo "🚀 Starting TypTalk..."
echo ""

# Stop oude processen
pkill -f typtalk 2>/dev/null || true
sleep 1

# Start daemon
./venv/bin/python3 typtalk_daemon_v2.py > typtalk_daemon.log 2>&1 &
sleep 3

# Save PID
pgrep -f typtalk_daemon_v2 > ~/.typtalk_pid

# Start listener
./typtalk_hotkey_listener > typtalk_listener.log 2>&1 &
sleep 2

# Verify
if pgrep -f typtalk_daemon_v2 > /dev/null && pgrep -f typtalk_hotkey_listener > /dev/null; then
    echo "✅ TypTalk is RUNNING!"
    echo ""
    echo "Hotkey: Rechter Alt/Option (⌥)"
    echo "Microfoon: MacBook Pro (niet koptelefoon!)"
    echo "Max: 20 seconden per opname"
    echo ""
    echo "Stop: ./STOP.sh"
    echo "Logs: tail -f typtalk_daemon.log"
else
    echo "❌ Failed to start"
    echo ""
    echo "Check logs:"
    echo "  tail -20 typtalk_daemon.log"
fi
