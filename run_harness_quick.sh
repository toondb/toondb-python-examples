#!/bin/bash
# Quick test runner for SochDB Test Harness v2.0 (Real LLM Mode)
# ================================================================

echo "======================================================================"
echo "SochDB Test Harness v2.0 - Quick Test (Real LLM Mode)"
echo "======================================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Create a .env file with your Azure OpenAI credentials:"
    echo ""
    echo "AZURE_OPENAI_API_KEY=your_key_here"
    echo "AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/"
    echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small"
    echo "AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4"
    echo "AZURE_OPENAI_API_VERSION=2024-12-01-preview"
    echo ""
    exit 1
fi

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ ERROR: openai package not installed"
    echo "Run: pip install -r harness_requirements.txt"
    exit 1
fi

python3 -c "import dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ ERROR: python-dotenv package not installed"
    echo "Run: pip install -r harness_requirements.txt"
    exit 1
fi

python3 -c "import numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ ERROR: numpy package not installed"
    echo "Run: pip install -r harness_requirements.txt"
    exit 1
fi

echo "✓ Dependencies OK"
echo ""

# Run quick test (2 scenarios only)
echo "Running quick test with 2 scenarios..."
echo "This will use REAL Azure OpenAI API calls"
echo ""

python3 harness_v2_real_llm.py \
    --scenarios 01_multi_tenant 02_sales_crm \
    --seed 42 \
    --scale small \
    --output quick_test_scorecard.json

echo ""
echo "======================================================================"
echo "Quick test complete!"
echo "Check quick_test_scorecard.json for detailed results"
echo "======================================================================"
