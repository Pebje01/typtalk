#!/bin/bash
# Installeer auto-start bij login

PLIST="$HOME/Library/LaunchAgents/com.typtalk.daemon.plist"

cat > "$PLIST" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.typtalk.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/daleyjansen_1/Documents/Repos/typtalk/START_TYPTALK.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
PLIST

launchctl load "$PLIST"

echo "✅ Auto-start geïnstalleerd!"
echo "TypTalk start nu automatisch na reboot"
