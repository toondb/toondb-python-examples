#!/bin/bash

# Start ToonDB server in IPC mode for multi-process incident response demo

DB_PATH="./ops_db"
SOCKET_PATH="${DB_PATH}/toondb.sock"

echo "=========================================="
echo "ToonDB IPC Server for Incident Response"
echo "=========================================="

# Check if toondb-server is available
if ! command -v toondb-server &> /dev/null; then
    echo "❌ Error: toondb-server not found in PATH"
    echo "Please install ToonDB or add it to your PATH"
    exit 1
fi

# Create DB directory if it doesn't exist
mkdir -p "$DB_PATH"

# Stop any existing server
if [ -e "$SOCKET_PATH" ]; then
    echo "🛑 Stopping existing server..."
    toondb-server stop --db "$DB_PATH" 2>/dev/null || true
    sleep 1
fi

# Start server
echo "🚀 Starting ToonDB server at $DB_PATH..."
toondb-server --db "$DB_PATH" &

# Wait for server to be ready
sleep 2

# Check status
echo ""
echo "Checking server status..."
toondb-server status --db "$DB_PATH"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ToonDB server is running!"
    echo "   Socket: $SOCKET_PATH"
    echo ""
    echo "You can now run the incident response processes:"
    echo "  1. python process_a_collector.py (metrics collector)"
    echo "  2. python process_b_indexer.py (runbook indexer)"
    echo "  3. python process_c_commander.py (incident commander)"
    echo ""
    echo "Press Ctrl+C to stop the server"
    
    # Keep script running
    wait
else
    echo "❌ Failed to start server"
    exit 1
fi
