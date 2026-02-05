#!/bin/bash
# TypTalk - Stop script

echo "🛑 Stopping TypTalk..."
pkill -f typtalk
rm -f ~/.typtalk_pid
sleep 1
echo "✅ Stopped"
