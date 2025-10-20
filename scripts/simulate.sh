#!/bin/bash

echo "🚁 Drone Consensus Blockchain - Simulation Script"
echo "================================================="

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "🎯 Available simulations:"
echo "1. Multi-entity simulation (10 entities)"
echo "2. Conflict detection simulation"
echo "3. Economic model simulation"
echo "4. Stress test simulation"
echo ""

read -p "Select simulation (1-4): " choice

case $choice in
    1)
        echo "🚁 Running multi-entity simulation..."
        if [ -f "tests/simulation/fixed_multi_entity_simulation.sh" ]; then
            ./tests/simulation/fixed_multi_entity_simulation.sh
        else
            echo "❌ Multi-entity simulation not found"
        fi
        ;;
    2)
        echo "⚠️ Running conflict detection simulation..."
        if [ -f "tests/simulation/run_multi_entity_simulation.sh" ]; then
            ./tests/simulation/run_multi_entity_simulation.sh
        else
            echo "❌ Conflict detection simulation not found"
        fi
        ;;
    3)
        echo "💰 Running economic model simulation..."
        if [ -f "tests/simulate_10_entities.py" ]; then
            python3 tests/simulate_10_entities.py
        else
            echo "❌ Economic model simulation not found"
        fi
        ;;
    4)
        echo "🚀 Running stress test simulation..."
        if [ -f "tests/stress_test_lab.py" ]; then
            python3 tests/stress_test_lab.py
        else
            echo "❌ Stress test simulation not found"
        fi
        ;;
    *)
        echo "❌ Invalid selection"
        exit 1
        ;;
esac

echo ""
echo "📊 Simulation completed!"
echo "📄 Check simulation reports in the current directory"
