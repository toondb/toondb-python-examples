#!/bin/bash

# Run all three processes for the incident response demo

DB_PATH="./ops_db"

echo "=========================================="
echo "Multi-Agent Incident Response Demo"
echo "=========================================="
echo ""
echo "This demo showcases:"
echo "  ✓ IPC mode: shared ToonDB across processes"
echo "  ✓ Namespace isolation"
echo "  ✓ Hybrid retrieval (vector + keyword with RRF)"
echo "  ✓ ACID state transitions"
echo ""
echo "Starting 3 processes:"
echo "  A. Metrics Collector (writes metrics to shared DB)"
echo "  B. Runbook Indexer (indexes runbooks to vector collection)"
echo "  C. Incident Commander (monitors metrics + retrieves runbooks)"
echo ""
echo "=========================================="
echo ""

# Check if server is running
if ! toondb-server status --db "$DB_PATH" &> /dev/null; then
    echo "⚠️  ToonDB server not detected. Starting server first..."
    ./start_server.sh &
    sleep 3
fi

echo "Starting processes in background..."
echo ""

# Start Process B (indexer) first to populate runbooks
echo "Starting Process B (Runbook Indexer)..."
python process_b_indexer.py > logs_process_b.txt 2>&1 &
PID_B=$!
echo "  → PID: $PID_B"
sleep 3

# Start Process A (collector)
echo "Starting Process A (Metrics Collector)..."
python process_a_collector.py > logs_process_a.txt 2>&1 &
PID_A=$!
echo "  → PID: $PID_A"
sleep 2

# Start Process C (commander) in foreground
echo "Starting Process C (Incident Commander)..."
echo ""
echo "=========================================="
echo ""

# Trap Ctrl+C to kill all processes
trap "echo ''; echo 'Stopping all processes...'; kill $PID_A $PID_B 2>/dev/null; exit" INT

python process_c_commander.py

# Cleanup
kill $PID_A $PID_B 2>/dev/null
echo ""
echo "All processes stopped."
