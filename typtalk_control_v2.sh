#!/bin/bash
# TypTalk V2 Control - Signal-based (with logging)

PID_FILE="$HOME/.typtalk_pid"
LOG_FILE="$HOME/Documents/Repos/typtalk/control.log"
COMMAND="$1"

echo "$(date): Control script called with: $COMMAND" >> "$LOG_FILE"

if [ ! -f "$PID_FILE" ]; then
    echo "$(date): ERROR - no PID file" >> "$LOG_FILE"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo "$(date): ERROR - PID $PID dead" >> "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

case "$COMMAND" in
    start)
        echo "$(date): Sending START to PID $PID" >> "$LOG_FILE"
        kill -SIGUSR1 "$PID"
        ;;
    stop)
        echo "$(date): Sending STOP to PID $PID" >> "$LOG_FILE"
        kill -SIGUSR2 "$PID"
        ;;
    quit)
        kill -SIGTERM "$PID"
        ;;
    *)
        echo "$(date): ERROR - unknown command: $COMMAND" >> "$LOG_FILE"
        exit 1
        ;;
esac
