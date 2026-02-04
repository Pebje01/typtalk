#!/bin/bash
# Stress test - 10 snelle opnames achter elkaar

echo "🧪 Stabiliteitstest - 10 snelle opnames"
echo "Dit zou de oude versie crashen, nieuwe moet het aankunnen"
echo ""

PID_FILE="$HOME/.typtalk_pid"
if [ ! -f "$PID_FILE" ]; then
    echo "❌ Daemon niet gestart"
    exit 1
fi

PID=$(cat "$PID_FILE")

for i in {1..10}; do
    echo "Test $i/10..."
    kill -SIGUSR1 "$PID"  # Start
    sleep 0.5
    kill -SIGUSR2 "$PID"  # Stop
    sleep 0.3
done

echo ""
if kill -0 "$PID" 2>/dev/null; then
    echo "✅ GESLAAGD! Daemon draait nog na stress test"
else
    echo "❌ GEFAALD! Daemon is gecrashed"
fi
