#!/bin/bash

echo "🧹 Drone Consensus Blockchain - Cleanup Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "🗑️ Cleaning up temporary files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.log" -delete
find . -name "*.tmp" -delete
find . -name ".DS_Store" -delete

echo "📁 Organizing remaining files..."
# Move any remaining loose files to appropriate directories
if [ -f "*.py" ]; then
    mv *.py src/ 2>/dev/null || true
fi

if [ -f "*.sh" ]; then
    mv *.sh scripts/ 2>/dev/null || true
fi

if [ -f "*.md" ]; then
    mv *.md docs/ 2>/dev/null || true
fi

echo "🔧 Updating file permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x tests/*.sh 2>/dev/null || true
chmod +x examples/*.sh 2>/dev/null || true

echo "📊 Generating project structure report..."
echo "Project Structure:" > project_structure.txt
echo "=================" >> project_structure.txt
tree -I 'venv|node_modules|__pycache__|.git' >> project_structure.txt 2>/dev/null || find . -type d | grep -v -E '(venv|node_modules|__pycache__|\.git)' | sort >> project_structure.txt

echo "✅ Cleanup complete!"
echo ""
echo "📁 Project structure:"
echo "===================="
if command -v tree >/dev/null 2>&1; then
    tree -I 'venv|node_modules|__pycache__|.git' -L 3
else
    find . -maxdepth 3 -type d | grep -v -E '(venv|node_modules|__pycache__|\.git)' | sort
fi

echo ""
echo "📄 Project structure saved to: project_structure.txt"
echo "🎯 Your repository is now clean and organized!"
