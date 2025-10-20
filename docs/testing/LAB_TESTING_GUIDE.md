# 🧪 Lab Testing Guide - Drone Consensus Blockchain

## 📋 **Complete Testing Framework for Your Lab**

This guide provides comprehensive testing procedures for your drone consensus blockchain system, designed for research lab validation and demonstration.

---

## 🎯 **Testing Objectives**

### **Primary Goals:**
- ✅ Validate Hedera Hashgraph integration
- ✅ Test flight plan consensus mechanisms
- ✅ Verify conflict detection algorithms
- ✅ Assess system performance under load
- ✅ Demonstrate economic model (FTC tokens)
- ✅ Prepare for research presentation

---

## 🚀 **Quick Start Testing**

### **1. Quick Lab Test (5 minutes)**
```bash
# Run basic functionality test
./quick_lab_test.sh
```
**What it tests:**
- Hedera node connectivity
- Environment configuration
- Basic flight plan submission
- API functionality
- Conflict detection

### **2. Comprehensive Test Suite (15 minutes)**
```bash
# Run full test suite
python lab_test_suite.py
```
**What it tests:**
- All system components
- End-to-end workflows
- API endpoints
- Hedera integration
- Generates detailed report

### **3. Stress Testing (30 minutes)**
```bash
# Run performance stress tests
python stress_test_lab.py
```
**What it tests:**
- Concurrent submissions
- High-frequency operations
- Memory usage
- Network performance
- System scalability

---

## 🧪 **Detailed Test Procedures**

### **Test 1: Hedera Node Validation**
```bash
# Check if Hedera node is running
curl http://127.0.0.1:5600/api/v1/status

# Expected: HTTP 200 with node status
```

### **Test 2: Environment Setup**
```bash
# Verify environment configuration
cd hedera-scripts
node connect_test.js

# Expected: "Connected to local Hedera node successfully!"
```

### **Test 3: Flight Plan Submission**
```bash
# Test Hedera flight plan submission
node submit_flightplan.js

# Expected: Flight plan submitted with transaction ID
```

### **Test 4: API Integration**
```bash
# Start API server
python hedera_flight_api.py &

# Test API health
curl http://127.0.0.1:8000/hedera/status

# Submit flight plan via API
curl -X POST http://127.0.0.1:8000/flightplan \
  -H "Content-Type: application/json" \
  -d '{
    "droneId": "lab_test_drone",
    "start": "2025-01-15T22:00:00Z",
    "end": "2025-01-15T22:30:00Z",
    "path": [[36.12, -86.67], [36.15, -86.70]]
  }'
```

### **Test 5: Conflict Detection**
```bash
# Submit conflicting flight plans
curl -X POST http://127.0.0.1:8000/flightplan \
  -H "Content-Type: application/json" \
  -d '{
    "droneId": "conflict_test_1",
    "start": "2025-01-15T23:00:00Z",
    "end": "2025-01-15T23:30:00Z",
    "path": [[36.12, -86.67], [36.15, -86.70]]
  }'

curl -X POST http://127.0.0.1:8000/flightplan \
  -H "Content-Type: application/json" \
  -d '{
    "droneId": "conflict_test_2",
    "start": "2025-01-15T23:15:00Z",
    "end": "2025-01-15T23:45:00Z",
    "path": [[36.13, -86.68], [36.16, -86.71]]
  }'

# Expected: Second submission should be DENIED due to conflict
```

---

## 📊 **Test Results Interpretation**

### **Success Criteria:**
- ✅ **Hedera Node**: Accessible and responding
- ✅ **Environment**: All variables configured
- ✅ **SDK Connectivity**: Successful connection
- ✅ **Flight Plans**: Submissions working
- ✅ **API Health**: All endpoints responding
- ✅ **Conflict Detection**: Overlaps properly detected
- ✅ **Performance**: < 2s response times
- ✅ **Memory**: Stable usage under load

### **Performance Benchmarks:**
| Test              | Target | Excellent | Good  | Needs Work |
| ----------------- | ------ | --------- | ----- | ---------- |
| API Response Time | < 2s   | < 1s      | < 2s  | > 2s       |
| Concurrent Users  | 10+    | 20+       | 10+   | < 10       |
| Submissions/sec   | 5+     | 10+       | 5+    | < 5        |
| Memory Usage      | < 20%  | < 10%     | < 20% | > 20%      |
| Success Rate      | > 95%  | > 98%     | > 95% | < 95%      |

---

## 🔧 **Troubleshooting Guide**

### **Common Issues & Solutions:**

#### **Issue: Hedera Node Not Running**
```bash
# Solution: Start Hedera node
cd hedera-local-node
docker compose up -d
# Wait 2-3 minutes for full startup
```

#### **Issue: Environment Not Configured**
```bash
# Solution: Run environment setup
cd hedera-scripts
node setup_environment.js
# Copy generated values to .env file
```

#### **Issue: API Not Responding**
```bash
# Solution: Check if API is running
ps aux | grep hedera_flight_api
# If not running: python hedera_flight_api.py
```

#### **Issue: Flight Plans Not Submitting**
```bash
# Solution: Check Hedera connectivity
cd hedera-scripts
node connect_test.js
# Verify .env file has correct values
```

#### **Issue: Conflicts Not Detected**
```bash
# Solution: Check blockchain state
curl http://127.0.0.1:8000/chain
# Verify time overlap in test data
```

---

## 📈 **Advanced Testing Scenarios**

### **Scenario 1: High-Volume Testing**
```bash
# Test with 100 concurrent flight plans
python -c "
import requests
import threading
import time

def submit_plan(i):
    plan = {
        'droneId': f'bulk_test_{i}',
        'start': '2025-01-15T24:00:00Z',
        'end': '2025-01-15T24:30:00Z',
        'path': [[36.12, -86.67], [36.15, -86.70]]
    }
    response = requests.post('http://127.0.0.1:8000/flightplan', json=plan)
    print(f'Plan {i}: {response.status_code}')

threads = []
for i in range(100):
    t = threading.Thread(target=submit_plan, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
"
```

### **Scenario 2: Economic Model Testing**
```bash
# Test FTC token economy
cd hedera-scripts

# Check FTC balance before
node -e "
const { Client, AccountBalanceQuery } = require('@hashgraph/sdk');
const client = Client.forNetwork({'127.0.0.1:50211': '0.0.3'});
client.setOperator(process.env.STAKER_ID, process.env.STAKER_KEY);
new AccountBalanceQuery().setAccountId(process.env.STAKER_ID).execute(client)
  .then(balance => console.log('FTC Balance:', balance.tokens._map.get(process.env.FTC_TOKEN_ID)));
"

# Submit flight plan (costs 10 FTC)
node submit_flightplan.js

# Check FTC balance after
node -e "
const { Client, AccountBalanceQuery } = require('@hashgraph/sdk');
const client = Client.forNetwork({'127.0.0.1:50211': '0.0.3'});
client.setOperator(process.env.STAKER_ID, process.env.STAKER_KEY);
new AccountBalanceQuery().setAccountId(process.env.STAKER_ID).execute(client)
  .then(balance => console.log('FTC Balance:', balance.tokens._map.get(process.env.FTC_TOKEN_ID)));
"
```

### **Scenario 3: Real-Time Monitoring**
```bash
# Start message consumer for real-time conflict detection
cd hedera-scripts
node consume_flightplans.js &

# In another terminal, submit flight plans
curl -X POST http://127.0.0.1:8000/flightplan \
  -H "Content-Type: application/json" \
  -d '{"droneId": "monitor_test", "start": "2025-01-15T25:00:00Z", "end": "2025-01-15T25:30:00Z", "path": [[36.12, -86.67], [36.15, -86.70]]}'
```

---

## 📋 **Lab Testing Checklist**

### **Pre-Test Setup:**
- [ ] Hedera node running (`docker compose ps`)
- [ ] Environment configured (`.env` file present)
- [ ] Dependencies installed (`npm install`, `pip install -r requirements.txt`)
- [ ] Network connectivity verified
- [ ] Test data prepared

### **Core Functionality Tests:**
- [ ] Hedera node connectivity
- [ ] SDK connection test
- [ ] Flight plan submission
- [ ] API health check
- [ ] Conflict detection
- [ ] Blockchain chain retrieval
- [ ] FTC token economy

### **Performance Tests:**
- [ ] Concurrent submissions
- [ ] High-frequency operations
- [ ] Memory usage monitoring
- [ ] Response time measurement
- [ ] Network performance

### **Integration Tests:**
- [ ] End-to-end workflow
- [ ] API endpoint validation
- [ ] Hedera consensus verification
- [ ] Economic model validation
- [ ] Error handling

---

## 🎯 **Research Presentation Preparation**

### **Demo Script for Lab:**
1. **Show the Problem**: Drone conflicts in airspace
2. **Present the Solution**: Blockchain consensus system
3. **Live Demo**: Real flight plan submission
4. **Show Consensus**: Hedera network agreement
5. **Demonstrate Conflicts**: Prevent dangerous overlaps
6. **Explain Economics**: FTC token incentives
7. **Discuss Scalability**: Production deployment

### **Key Metrics to Highlight:**
- **Consensus Time**: < 3 seconds
- **Conflict Detection**: 100% accuracy
- **Economic Model**: Pay-to-submit incentives
- **Scalability**: 10+ concurrent users
- **Reliability**: Hedera network consensus

---

## 📄 **Test Reports Generated**

1. **`lab_test_report.txt`** - Comprehensive test results
2. **`stress_test_report.txt`** - Performance analysis
3. **Console output** - Real-time test feedback
4. **Log files** - Detailed execution logs

---

## 🚀 **Next Steps After Testing**

1. **Review Results**: Analyze test reports
2. **Fix Issues**: Address any failures
3. **Optimize Performance**: Improve bottlenecks
4. **Prepare Demo**: Practice presentation
5. **Document Findings**: Record research insights

---

**🎉 Your lab testing framework is ready! Run the tests and demonstrate your innovative drone consensus blockchain system to your research team! 🚁✈️**
