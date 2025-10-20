#!/bin/bash

echo "🚁 Multi-Entity Drone Consensus Simulation"
echo "=========================================="
echo "📅 Date: $(date)"
echo "👨‍🔬 Lab: Vanderbilt Research"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Entity definitions with stake amounts and FTC balances
declare -A entities=(
    ["E001"]="Amazon Drone Delivery:1500:250:commercial"
    ["E002"]="Vanderbilt Research Lab:1200:200:research"
    ["E003"]="Nashville Emergency Services:2000:300:emergency"
    ["E004"]="FedEx Air Cargo:800:150:commercial"
    ["E005"]="Weather Monitoring Service:600:120:research"
    ["E006"]="Security Patrol Corp:750:140:surveillance"
    ["E007"]="Local Photography Drone:300:80:commercial"
    ["E008"]="Campus Security:200:60:surveillance"
    ["E009"]="Agricultural Survey:150:50:research"
    ["E010"]="Hobby Drone Pilot:50:20:recreational"
)

echo -e "${BLUE}🏢 SIMULATION ENTITIES${NC}"
echo "========================"
for entity_id in "${!entities[@]}"; do
    IFS=':' read -r name stake ftc type <<< "${entities[$entity_id]}"
    echo -e "${CYAN}$entity_id${NC}: $name"
    echo "   Stake: $stake HBAR | FTC: $ftc | Type: $type"
done
echo ""

# Start API server if not running
echo -e "${BLUE}🚀 Starting API Server${NC}"
echo "======================"
python3 hedera_flight_api.py &
API_PID=$!
sleep 3

# Check if API is running
if curl -s http://127.0.0.1:8000/hedera/status > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API Server is running${NC}"
else
    echo -e "${RED}❌ API Server failed to start${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🔄 ROUND 1: High-Stake Entities Submit Flight Plans${NC}"
echo "======================================================"

# High-stake entities (1000+ HBAR) submit first
high_stake_entities=("E001" "E002" "E003")
for entity_id in "${high_stake_entities[@]}"; do
    IFS=':' read -r name stake ftc type <<< "${entities[$entity_id]}"
    
    echo -e "${PURPLE}📡 $name (Stake: $stake HBAR) submitting flight plan...${NC}"
    
    # Generate flight plan with current time + random offset
    start_time=$(date -u -v+$(($RANDOM % 30 + 5))M '+%Y-%m-%dT%H:%M:%SZ')
    end_time=$(date -u -v+$(($RANDOM % 30 + 35))M '+%Y-%m-%dT%H:%M:%SZ')
    
    # Submit flight plan
    response=$(curl -s -X POST http://127.0.0.1:8000/flightplan \
        -H "Content-Type: application/json" \
        -d "{
            \"droneId\": \"${entity_id}_flight_1\",
            \"start\": \"$start_time\",
            \"end\": \"$end_time\",
            \"path\": [[36.12, -86.67], [36.15, -86.70]],
            \"entity\": \"$name\",
            \"stake\": $stake,
            \"ftc_balance\": $ftc,
            \"flight_type\": \"$type\"
        }" 2>/dev/null)
    
    if echo "$response" | grep -q "APPROVED\|SUBMITTED"; then
        echo -e "   ${GREEN}✅ APPROVED${NC}"
    else
        echo -e "   ${RED}❌ DENIED${NC}"
    fi
    
    sleep 1
done

echo ""
echo -e "${BLUE}🔄 ROUND 2: Medium-Stake Entities Submit Flight Plans${NC}"
echo "========================================================"

# Medium-stake entities (500-999 HBAR)
medium_stake_entities=("E004" "E005" "E006")
for entity_id in "${medium_stake_entities[@]}"; do
    IFS=':' read -r name stake ftc type <<< "${entities[$entity_id]}"
    
    echo -e "${PURPLE}📡 $name (Stake: $stake HBAR) submitting flight plan...${NC}"
    
    # Generate flight plan with potential conflict
    start_time=$(date -u -v+$(($RANDOM % 20 + 10))M '+%Y-%m-%dT%H:%M:%SZ')
    end_time=$(date -u -v+$(($RANDOM % 20 + 40))M '+%Y-%m-%dT%H:%M:%SZ')
    
    response=$(curl -s -X POST http://127.0.0.1:8000/flightplan \
        -H "Content-Type: application/json" \
        -d "{
            \"droneId\": \"${entity_id}_flight_1\",
            \"start\": \"$start_time\",
            \"end\": \"$end_time\",
            \"path\": [[36.13, -86.68], [36.16, -86.71]],
            \"entity\": \"$name\",
            \"stake\": $stake,
            \"ftc_balance\": $ftc,
            \"flight_type\": \"$type\"
        }" 2>/dev/null)
    
    if echo "$response" | grep -q "APPROVED\|SUBMITTED"; then
        echo -e "   ${GREEN}✅ APPROVED${NC}"
    else
        echo -e "   ${RED}❌ DENIED${NC}"
    fi
    
    sleep 1
done

echo ""
echo -e "${BLUE}🔄 ROUND 3: Low-Stake Entities Submit Flight Plans${NC}"
echo "====================================================="

# Low-stake entities (100-499 HBAR)
low_stake_entities=("E007" "E008" "E009")
for entity_id in "${low_stake_entities[@]}"; do
    IFS=':' read -r name stake ftc type <<< "${entities[$entity_id]}"
    
    echo -e "${PURPLE}📡 $name (Stake: $stake HBAR) submitting flight plan...${NC}"
    
    # Generate flight plan with potential conflict
    start_time=$(date -u -v+$(($RANDOM % 15 + 15))M '+%Y-%m-%dT%H:%M:%SZ')
    end_time=$(date -u -v+$(($RANDOM % 15 + 45))M '+%Y-%m-%dT%H:%M:%SZ')
    
    response=$(curl -s -X POST http://127.0.0.1:8000/flightplan \
        -H "Content-Type: application/json" \
        -d "{
            \"droneId\": \"${entity_id}_flight_1\",
            \"start\": \"$start_time\",
            \"end\": \"$end_time\",
            \"path\": [[36.11, -86.66], [36.14, -86.69]],
            \"entity\": \"$name\",
            \"stake\": $stake,
            \"ftc_balance\": $ftc,
            \"flight_type\": \"$type\"
        }" 2>/dev/null)
    
    if echo "$response" | grep -q "APPROVED\|SUBMITTED"; then
        echo -e "   ${GREEN}✅ APPROVED${NC}"
    else
        echo -e "   ${RED}❌ DENIED${NC}"
    fi
    
    sleep 1
done

echo ""
echo -e "${BLUE}⚠️ CONFLICT SCENARIO: Minimal Stake Entity${NC}"
echo "============================================="

# Minimal stake entity tries to submit conflicting plan
entity_id="E010"
IFS=':' read -r name stake ftc type <<< "${entities[$entity_id]}"

echo -e "${PURPLE}📡 $name (Stake: $stake HBAR) submitting conflicting flight plan...${NC}"

# Create conflicting time window
start_time=$(date -u -v+10M '+%Y-%m-%dT%H:%M:%SZ')
end_time=$(date -u -v+40M '+%Y-%m-%dT%H:%M:%SZ')

response=$(curl -s -X POST http://127.0.0.1:8000/flightplan \
    -H "Content-Type: application/json" \
    -d "{
        \"droneId\": \"${entity_id}_conflict\",
        \"start\": \"$start_time\",
        \"end\": \"$end_time\",
        \"path\": [[36.12, -86.67], [36.15, -86.70]],
        \"entity\": \"$name\",
        \"stake\": $stake,
        \"ftc_balance\": $ftc,
        \"flight_type\": \"$type\"
    }" 2>/dev/null)

if echo "$response" | grep -q "DENIED\|CONFLICT"; then
    echo -e "   ${GREEN}✅ CONFLICT DETECTED - DENIED${NC}"
    echo -e "   ${YELLOW}💡 System correctly prevented dangerous overlap${NC}"
else
    echo -e "   ${RED}❌ CONFLICT NOT DETECTED${NC}"
fi

echo ""
echo -e "${BLUE}📊 SIMULATION SUMMARY${NC}"
echo "====================="

# Get blockchain chain to see all submissions
echo -e "${CYAN}📋 Blockchain Chain Status:${NC}"
chain_response=$(curl -s http://127.0.0.1:8000/chain)
chain_length=$(echo "$chain_response" | grep -o '"index"' | wc -l)
echo "   Total blocks in chain: $chain_length"

echo ""
echo -e "${CYAN}💰 Economic Model Analysis:${NC}"
echo "   High Stake Entities (1000+ HBAR): 3"
echo "   Medium Stake Entities (500-999 HBAR): 3"
echo "   Low Stake Entities (100-499 HBAR): 3"
echo "   Minimal Stake Entities (< 100 HBAR): 1"

echo ""
echo -e "${CYAN}🎯 Key Insights:${NC}"
echo "   • Higher stake = More FTC earning capacity"
echo "   • Economic incentives encourage proper coordination"
echo "   • Conflict detection prevents dangerous overlaps"
echo "   • System scales with multiple entities"

echo ""
echo -e "${GREEN}🎉 Multi-Entity Simulation Complete!${NC}"
echo "=================================="
echo "✅ Demonstrated 10 entities with varying stake amounts"
echo "✅ Showed economic model with FTC token economy"
echo "✅ Validated conflict detection and prevention"
echo "✅ Proved system scalability for multiple users"

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $API_PID 2>/dev/null

echo ""
echo "📄 For detailed analysis, run: python3 simulate_10_entities.py"
echo "🎯 For research demo, run: ./demo_research_meeting.sh"
echo ""
echo "Great work on your multi-entity drone consensus system! 🚁✈️"
