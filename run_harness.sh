#!/bin/bash
# Run SochDB Comprehensive Test Harness
# Usage: ./run_harness.sh [small|medium|large] [embedded|server]

set -e

SCALE=${1:-medium}
MODE=${2:-embedded}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="harness_results"
OUTPUT_FILE="${OUTPUT_DIR}/scorecard_${SCALE}_${MODE}_${TIMESTAMP}.json"

echo "=========================================="
echo "SochDB Comprehensive Test Harness"
echo "=========================================="
echo "Scale: $SCALE"
echo "Mode: $MODE"
echo "Output: $OUTPUT_FILE"
echo "=========================================="
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if SDK is installed
if ! python -c "import sochdb" 2>/dev/null; then
    echo "❌ SochDB SDK not found. Installing..."
    pip install -e ../sochdb-python-sdk
fi

# Check dependencies
if ! python -c "import numpy, dotenv" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r harness_requirements.txt
fi

# Clean up old test data
rm -rf test_harness_db/

# Run harness
echo "🚀 Starting harness..."
python comprehensive_harness.py \
    --scale "$SCALE" \
    --mode "$MODE" \
    --seed 1337 \
    --output "$OUTPUT_FILE"

EXIT_CODE=$?

# Summary
echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests PASSED"
    SCORE=$(python -c "import json; print(json.load(open('$OUTPUT_FILE'))['overall']['score_0_100'])")
    echo "📊 Overall Score: $SCORE/100"
else
    echo "❌ Some tests FAILED"
    echo "📄 Check details in: $OUTPUT_FILE"
fi
echo "=========================================="

exit $EXIT_CODE
