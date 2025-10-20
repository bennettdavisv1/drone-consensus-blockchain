#!/bin/bash

echo "🧪 Quick Lab Test - Drone Consensus Blockchain"
echo "=============================================="
echo "📅 Date: $(date)"
echo "👨‍🔬 Lab: Vanderbilt Research"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

test_passed() {
    echo -e "${GREEN}✅ $1${NC}"
}

test_failed() {
    echo -e "${RED}❌ $1${NC}"
}

test_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo -e "${BLUE}🔍 TESTING HEDERA NODE CONNECTIVITY${NC}"
echo "=================================="

# Test 1: Check if Hedera node is running
if curl -s http://127.0.0.1:5600/api/v1/status > /dev/null 2>&1; then
    test_passed "Hedera node is running and accessible"
    HEDERA_RUNNING=true
else
    test_failed "Hedera node is not running"
    echo "💡 Start with: cd hedera-local-node && docker compose up -d"
    HEDERA_RUNNING=false
fi

echo ""
echo -e "${BLUE}🔧 TESTING HEDERA ENVIRONMENT${NC}"
echo "==============================="

# Test 2: Check environment setup
if [ -f "hedera-scripts/.env" ]; then
    if grep -q "FTC_TOKEN_ID" hedera-scripts/.env && grep -q "FLIGHT_PLAN_TOPIC_ID" hedera-scripts/.env; then
        test_passed "Hedera environment is configured"
        ENV_CONFIGURED=true
    else
        test_warning "Environment file exists but missing required variables"
        ENV_CONFIGURED=false
    fi
else
    test_failed "Environment file not found"
    echo "💡 Run: cd hedera-scripts && node setup_environment.js"
    ENV_CONFIGURED=false
fi

echo ""
echo -e "${BLUE}🧪 TESTING HEDERA SDK${NC}"
echo "======================"

# Test 3: Test Hedera SDK connectivity
if [ "$HEDERA_RUNNING" = true ] && [ "$ENV_CONFIGURED" = true ]; then
    cd hedera-scripts
    if node connect_test.js > /dev/null 2>&1; then
        test_passed "Hedera SDK connectivity successful"
        SDK_WORKING=true
    else
        test_failed "Hedera SDK connectivity failed"
        SDK_WORKING=false
    fi
    cd ..
else
    test_warning "Skipping SDK test - prerequisites not met"
    SDK_WORKING=false
fi

echo ""
echo -e "${BLUE}✈️ TESTING FLIGHT PLAN SUBMISSION${NC}"
echo "=================================="

# Test 4: Test flight plan submission
if [ "$SDK_WORKING" = true ]; then
    cd hedera-scripts
    if node submit_flightplan.js > /dev/null 2>&1; then
        test_passed "Flight plan submission successful"
        SUBMISSION_WORKING=true
    else
        test_failed "Flight plan submission failed"
        SUBMISSION_WORKING=false
    fi
    cd ..
else
    test_warning "Skipping flight plan test - SDK not working"
    SUBMISSION_WORKING=false
fi

echo ""
echo -e "${BLUE}🌐 TESTING PYTHON API${NC}"
echo "======================"

# Test 5: Start and test Python API
echo "🚀 Starting Python API server..."
python hedera_flight_api.py &
API_PID=$!
sleep 3

# Test API health
if curl -s http://127.0.0.1:8000/hedera/status > /dev/null 2>&1; then
    test_passed "Python API is running and healthy"
    API_WORKING=true
else
    test_failed "Python API is not responding"
    API_WORKING=false
fi

# Test flight plan submission via API
if [ "$API_WORKING" = true ]; then
    echo "📡 Testing flight plan submission via API..."
    RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/flightplan \
        -H "Content-Type: application/json" \
        -d '{
            "droneId": "lab_test_drone",
            "start": "2025-01-15T21:00:00Z",
            "end": "2025-01-15T21:30:00Z",
            "path": [[36.12, -86.67], [36.15, -86.70]]
        }' 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "status"; then
        test_passed "API flight plan submission successful"
        API_SUBMISSION_WORKING=true
    else
        test_failed "API flight plan submission failed"
        API_SUBMISSION_WORKING=false
    fi
else
    test_warning "Skipping API submission test - API not working"
    API_SUBMISSION_WORKING=false
fi

# Test conflict detection
if [ "$API_WORKING" = true ]; then
    echo "⚠️ Testing conflict detection..."
    CONFLICT_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/flightplan \
        -H "Content-Type: application/json" \
        -d '{
            "droneId": "conflict_test_drone",
            "start": "2025-01-15T21:15:00Z",
            "end": "2025-01-15T21:45:00Z",
            "path": [[36.13, -86.68], [36.16, -86.71]]
        }' 2>/dev/null)
    
    if echo "$CONFLICT_RESPONSE" | grep -q "DENIED\|CONFLICT"; then
        test_passed "Conflict detection is working"
        CONFLICT_DETECTION_WORKING=true
    else
        test_warning "Conflict detection may not be working properly"
        CONFLICT_DETECTION_WORKING=false
    fi
else
    test_warning "Skipping conflict detection test - API not working"
    CONFLICT_DETECTION_WORKING=false
fi

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $API_PID 2>/dev/null

echo ""
echo -e "${BLUE}📊 LAB TEST SUMMARY${NC}"
echo "===================="

# Count results
TOTAL_TESTS=0
PASSED_TESTS=0

# Hedera tests
TOTAL_TESTS=$((TOTAL_TESTS + 1))
[ "$HEDERA_RUNNING" = true ] && PASSED_TESTS=$((PASSED_TESTS + 1))

TOTAL_TESTS=$((TOTAL_TESTS + 1))
[ "$ENV_CONFIGURED" = true ] && PASSED_TESTS=$((PASSED_TESTS + 1))

TOTAL_TESTS=$((TOTAL_TESTS + 1))
[ "$SDK_WORKING" = true ] && PASSED_TESTS=$((PASSED_TESTS + 1))

TOTAL_TESTS=$((TOTAL_TESTS + 1))
[ "$SUBMISSION_WORKING" = true ] && PASSED_TESTS=$((PASSED_TESTS + 1))

TOTAL_TESTS=$((TOTAL_TESTS + 1))
[ "$API_WORKING" = true ] && PASSED_TESTS=$((PASSED_TESTS + 1))

TOTAL_TESTS=$((TOTAL_TESTS + 1))
[ "$API_SUBMISSION_WORKING" = true ] && PASSED_TESTS=$((PASSED_TESTS + 1))

TOTAL_TESTS=$((TOTAL_TESTS + 1))
[ "$CONFLICT_DETECTION_WORKING" = true ] && PASSED_TESTS=$((PASSED_TESTS + 1))

SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))

echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Success Rate: $SUCCESS_RATE%"

if [ $SUCCESS_RATE -ge 80 ]; then
    echo -e "${GREEN}🎉 Lab test PASSED! System is ready for research demonstration.${NC}"
elif [ $SUCCESS_RATE -ge 60 ]; then
    echo -e "${YELLOW}⚠️ Lab test PARTIAL - Some issues detected but system is functional.${NC}"
else
    echo -e "${RED}❌ Lab test FAILED - System needs attention before demonstration.${NC}"
fi

echo ""
echo -e "${BLUE}🔗 NEXT STEPS${NC}"
echo "============="

if [ "$HEDERA_RUNNING" = false ]; then
    echo "1. Start Hedera node: cd hedera-local-node && docker compose up -d"
fi

if [ "$ENV_CONFIGURED" = false ]; then
    echo "2. Setup environment: cd hedera-scripts && node setup_environment.js"
fi

if [ $SUCCESS_RATE -ge 80 ]; then
    echo "3. Run full demo: ./demo_research_meeting.sh"
    echo "4. Run comprehensive tests: python lab_test_suite.py"
fi

echo ""
echo "📄 For detailed testing, run: python lab_test_suite.py"
echo "🎯 For research demo, run: ./demo_research_meeting.sh"
echo ""
echo "Good luck with your lab testing! 🚁✈️"
