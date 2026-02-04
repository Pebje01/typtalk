#!/bin/bash
# TypTalk V2 Control - Signal-based

PID_FILE="$HOME/.typtalk_pid"
COMMAND="$1"

if [ ! -f "$PID_FILE" ]; then
    echo "ERROR: Daemon not running (no PID file)"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo "ERROR: Daemon not running (PID $PID dead)"
    rm -f "$PID_FILE"
    exit 1
fi

case "$COMMAND" in
    start)
        kill -SIGUSR1 "$PID"
        ;;
    stop)
        kill -SIGUSR2 "$PID"
        ;;
    quit)
        kill -SIGTERM "$PID"
        ;;
    *)
        echo "Usage: $0 {start|stop|quit}"
        exit 1
        ;;
esac
