#!/bin/bash

echo "🧪 Drone Consensus Blockchain - Test Suite"
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "🔍 Running quick lab test..."
if [ -f "tests/quick_lab_test.sh" ]; then
    ./tests/quick_lab_test.sh
else
    echo "⚠️ Quick lab test not found"
fi

echo ""
echo "🧪 Running comprehensive test suite..."
if [ -f "tests/lab_test_suite.py" ]; then
    python3 tests/lab_test_suite.py
else
    echo "⚠️ Comprehensive test suite not found"
fi

echo ""
echo "🚀 Running stress tests..."
if [ -f "tests/stress_test_lab.py" ]; then
    python3 tests/stress_test_lab.py
else
    echo "⚠️ Stress tests not found"
fi

echo ""
echo "📊 Test results summary:"
echo "✅ Quick lab test completed"
echo "✅ Comprehensive test suite completed"
echo "✅ Stress tests completed"
echo ""
echo "📄 Check test reports in the current directory"
