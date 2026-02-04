#!/bin/bash
# TypTalk Control Script
# Stuurt commando's naar de daemon via FIFO pipe

PIPE="$HOME/.typtalk_control"
COMMAND="$1"

if [ -z "$COMMAND" ]; then
    echo "Usage: $0 {start|stop|quit}"
    exit 1
fi

if [ ! -p "$PIPE" ]; then
    echo "Error: Daemon not running (pipe not found)"
    exit 1
fi

# Stuur commando naar pipe
echo "$COMMAND" > "$PIPE"
