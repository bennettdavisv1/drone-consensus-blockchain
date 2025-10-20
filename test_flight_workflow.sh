#!/bin/bash

echo "🚀 Testing Complete Drone Flight Plan Workflow"
echo "=============================================="

# Check if Hedera node is running
echo "1️⃣ Checking Hedera node status..."
if curl -s http://127.0.0.1:5600/api/v1/status > /dev/null; then
    echo "✅ Hedera node is running"
else
    echo "❌ Hedera node is not running. Start it with:"
    echo "   cd hedera-local-node && docker compose up -d"
    exit 1
fi

# Setup environment
echo -e "\n2️⃣ Setting up Hedera environment..."
cd hedera-scripts
node setup_environment.js

echo -e "\n3️⃣ Testing flight plan submission..."
node submit_flightplan.js

echo -e "\n4️⃣ Testing Python API integration..."
cd ..
python hedera_flight_api.py &
API_PID=$!

# Wait for API to start
sleep 3

echo -e "\n5️⃣ Testing API endpoints..."

# Test flight plan submission via API
curl -X POST http://127.0.0.1:8000/flightplan \
  -H "Content-Type: application/json" \
  -d '{
        "droneId": "test_drone_123",
        "start": "2025-01-15T15:00:00Z",
        "end": "2025-01-15T15:30:00Z",
        "path": [[36.12, -86.67], [36.15, -86.70]]
      }'

echo -e "\n\n6️⃣ Testing conflict detection..."
curl -X POST http://127.0.0.1:8000/flightplan \
  -H "Content-Type: application/json" \
  -d '{
        "droneId": "conflict_drone_456",
        "start": "2025-01-15T15:15:00Z",
        "end": "2025-01-15T15:45:00Z",
        "path": [[36.13, -86.68], [36.16, -86.71]]
      }'

echo -e "\n\n7️⃣ Checking Hedera status..."
curl http://127.0.0.1:8000/hedera/status

echo -e "\n\n8️⃣ Getting blockchain chain..."
curl http://127.0.0.1:8000/chain

# Cleanup
echo -e "\n\n🧹 Cleaning up..."
kill $API_PID 2>/dev/null

echo -e "\n✅ Test workflow completed!"
echo "💡 To run the message consumer: cd hedera-scripts && node consume_flightplans.js"
