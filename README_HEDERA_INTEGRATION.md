# 🛰️ Hedera Flight Plan Integration

This document explains the complete Hedera Hashgraph integration for drone flight plan consensus.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python API    │    │  Hedera HCS     │    │  Message        │
│   (Flask)       │───▶│  Topic           │───▶│  Consumer       │
│                 │    │                  │    │  (Conflict      │
│                 │    │                  │    │   Detection)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Mock          │    │  FTC Token       │    │  Real-time      │
│   Blockchain    │    │  Economy         │    │  Consensus      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start Hedera Node
```bash
cd hedera-local-node
docker compose up -d
```

### 2. Setup Environment
```bash
cd hedera-scripts
node setup_environment.js
```

### 3. Update .env File
Add the generated values to your `.env` file:
```
OPERATOR_ID=0.0.2
OPERATOR_KEY=302e020100...
STAKER_ID=0.0.1002
STAKER_KEY=302e020100...
FTC_TOKEN_ID=0.0.1007
FLIGHT_PLAN_TOPIC_ID=0.0.1008
```

### 4. Test Complete Workflow
```bash
./test_flight_workflow.sh
```

## 📁 New Files Created

### Hedera Scripts
- **`setup_environment.js`** - Complete environment setup (accounts, tokens, topics)
- **`create_topic.js`** - Create HCS topic for flight plans
- **`submit_flightplan.js`** - Submit flight plans with FTC payment
- **`consume_flightplans.js`** - Real-time message consumption with conflict detection

### Python Integration
- **`hedera_flight_api.py`** - Enhanced Flask API with Hedera integration
- **`test_flight_workflow.sh`** - Complete end-to-end testing script

## 🔄 Workflow

### Flight Plan Submission
1. **API Request** → Python Flask receives flight plan
2. **Hedera Submission** → Flight plan sent to HCS topic
3. **FTC Payment** → Automatic token transfer for submission cost
4. **Consensus** → Hedera network reaches consensus on message order
5. **Conflict Detection** → Consumer checks for time/space conflicts
6. **Result** → APPROVED/DENIED status returned

### Key Features
- ✅ **Real Hedera Integration** - Uses actual Hedera Consensus Service
- ✅ **FTC Token Economy** - Pay-to-submit model with Flight Throughput Credits
- ✅ **Conflict Detection** - Real-time overlap detection
- ✅ **Immutable Records** - All submissions recorded on Hedera
- ✅ **Fallback Support** - Falls back to mock blockchain if Hedera fails

## 🧪 Testing

### Individual Components
```bash
# Test Hedera connectivity
node connect_test.js

# Create accounts and tokens
node setup_environment.js

# Submit a flight plan
node submit_flightplan.js

# Start message consumer
node consume_flightplans.js
```

### Complete Integration
```bash
# Run full workflow test
./test_flight_workflow.sh

# Start integrated API
python hedera_flight_api.py

# Test via API
curl -X POST http://127.0.0.1:8000/flightplan \
  -H "Content-Type: application/json" \
  -d '{"droneId": "test", "start": "2025-01-15T14:00:00Z", "end": "2025-01-15T14:30:00Z", "path": [[36.12, -86.67], [36.15, -86.70]]}'
```

## 🔧 API Endpoints

### Enhanced Endpoints
- **`POST /flightplan`** - Submit flight plan (Hedera + fallback)
- **`GET /chain`** - View blockchain (mock + Hedera records)
- **`GET /hedera/status`** - Check Hedera integration status
- **`POST /hedera/consume`** - Start message consumer

### Response Types
```json
// Hedera submission success
{
  "status": "SUBMITTED_TO_HEDERA",
  "message": "Flight plan submitted to Hedera Consensus Service",
  "transaction_id": "0.0.1002@1234567890.123456789",
  "ftc_cost": 10
}

// Mock blockchain fallback
{
  "status": "APPROVED",
  "message": "Approved"
}
```

## 🎯 Next Steps

### Phase 3: Dynamic FTC Minting
- Implement stake-based FTC minting
- Dynamic pricing based on network congestion
- Automated credit issuance

### Phase 4: Advanced Features
- Geographic conflict detection (spatial overlap)
- Multi-drone coordination
- Real-time dashboard
- Smart contract integration

## 🔒 Security Notes

- **Private Keys**: Never commit to repository
- **Environment Variables**: Use `.env` file for sensitive data
- **Network Security**: Local node for development only
- **Token Management**: FTC tokens are test tokens only

## 📊 Performance

- **Latency**: ~2-3 seconds for Hedera consensus
- **Throughput**: Limited by local node capacity
- **Scalability**: Production Hedera network supports millions of TPS
- **Cost**: FTC tokens for testing (no real HBAR cost)

---

**🎉 Congratulations!** You now have a complete drone consensus system running on Hedera Hashgraph with real blockchain consensus, token economy, and conflict detection!
