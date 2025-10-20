#!/bin/bash

echo "🚀 Drone Consensus Blockchain - Setup Script"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📁 Creating directory structure..."
mkdir -p src/{api,blockchain,hedera,testing}
mkdir -p docs/{api,testing,deployment}
mkdir -p config
mkdir -p scripts
mkdir -p tests/{unit,integration,simulation}
mkdir -p examples

echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "📦 Installing Node.js dependencies..."
if [ -d "src/hedera" ]; then
    cd src/hedera
    npm install
    cd ../..
fi

echo "🔧 Setting up Hedera node..."
if [ -d "hedera-local-node" ]; then
    cd hedera-local-node
    docker compose up -d
    echo "⏳ Waiting for Hedera node to start..."
    sleep 30
    cd ..
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run tests: ./scripts/test.sh"
echo "2. Start API: ./scripts/start-api.sh"
echo "3. Run simulation: ./scripts/simulate.sh"
echo ""
echo "📚 Documentation: docs/README.md"
