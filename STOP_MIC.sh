#!/bin/bash
# Emergency Stop - Stop microfoon onmiddellijk

echo "🛑 Emergency stop - microfoon stoppen..."
pkill -9 -f typtalk_daemon
pkill -9 -f typtalk_watchdog
rm -f ~/.typtalk_control
echo "✅ Alles gestopt!"
echo ""
echo "Herstart met: ./START_TYPTALK.sh"
