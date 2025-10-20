#!/usr/bin/env python3
"""
🚁 Multi-Entity Drone Consensus Simulation
==========================================

Simulates 10 different entities with varying stake amounts submitting flight plans:
- Different stake levels (affects FTC earning capacity)
- Various flight plan types (commercial, research, emergency)
- Time-based conflicts and resolutions
- Economic model demonstration
- Real-time consensus simulation

Usage: python3 simulate_10_entities.py
"""

import requests
import json
import time
import random
import threading
from datetime import datetime, timedelta
import concurrent.futures

class DroneEntity:
    def __init__(self, entity_id, name, stake_amount, entity_type, base_location):
        self.entity_id = entity_id
        self.name = name
        self.stake_amount = stake_amount  # HBAR staked
        self.entity_type = entity_type
        self.base_location = base_location
        self.ftc_balance = self.calculate_ftc_balance()
        self.flight_plans_submitted = 0
        self.flight_plans_approved = 0
        self.flight_plans_denied = 0
        
    def calculate_ftc_balance(self):
        """Calculate FTC balance based on stake amount"""
        # Higher stake = more FTC earning capacity
        if self.stake_amount >= 1000:
            return random.randint(200, 300)  # High staker
        elif self.stake_amount >= 500:
            return random.randint(100, 200)  # Medium staker
        elif self.stake_amount >= 100:
            return random.randint(50, 100)   # Low staker
        else:
            return random.randint(10, 50)    # Minimal staker
    
    def generate_flight_plan(self, flight_type="standard"):
        """Generate a flight plan based on entity type and location"""
        base_time = datetime.now() + timedelta(minutes=random.randint(5, 60))
        duration = self.get_flight_duration(flight_type)
        
        # Generate path based on entity type and base location
        start_lat, start_lon = self.base_location
        end_lat = start_lat + random.uniform(-0.1, 0.1)
        end_lon = start_lon + random.uniform(-0.1, 0.1)
        
        flight_plan = {
            "droneId": f"{self.entity_id}_{self.flight_plans_submitted + 1}",
            "start": base_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": (base_time + timedelta(minutes=duration)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "path": [[start_lat, start_lon], [end_lat, end_lon]],
            "entity": self.name,
            "stake": self.stake_amount,
            "ftc_balance": self.ftc_balance,
            "flight_type": flight_type,
            "priority": self.get_priority()
        }
        
        return flight_plan
    
    def get_flight_duration(self, flight_type):
        """Get flight duration based on type"""
        durations = {
            "emergency": random.randint(5, 15),
            "commercial": random.randint(20, 45),
            "research": random.randint(30, 90),
            "delivery": random.randint(10, 30),
            "surveillance": random.randint(15, 60),
            "standard": random.randint(15, 45)
        }
        return durations.get(flight_type, 30)
    
    def get_priority(self):
        """Get priority based on entity type and stake"""
        if self.entity_type == "emergency_services":
            return "HIGH"
        elif self.stake_amount >= 1000:
            return "HIGH"
        elif self.stake_amount >= 500:
            return "MEDIUM"
        else:
            return "LOW"
    
    def can_submit_flight(self, cost=10):
        """Check if entity has enough FTC to submit flight"""
        return self.ftc_balance >= cost
    
    def submit_flight(self, cost=10):
        """Submit flight and update balances"""
        if self.can_submit_flight(cost):
            self.ftc_balance -= cost
            self.flight_plans_submitted += 1
            return True
        return False

class MultiEntitySimulator:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.entities = self.create_entities()
        self.simulation_results = []
        self.api_process = None
        
    def create_entities(self):
        """Create 10 different entities with varying characteristics"""
        entities = [
            # High Stake Entities (1000+ HBAR)
            DroneEntity("E001", "Amazon Drone Delivery", 1500, "commercial", [36.12, -86.67]),
            DroneEntity("E002", "Vanderbilt Research Lab", 1200, "research", [36.12, -86.65]),
            DroneEntity("E003", "Nashville Emergency Services", 2000, "emergency_services", [36.12, -86.70]),
            
            # Medium Stake Entities (500-999 HBAR)
            DroneEntity("E004", "FedEx Air Cargo", 800, "commercial", [36.15, -86.70]),
            DroneEntity("E005", "Weather Monitoring Service", 600, "research", [36.13, -86.68]),
            DroneEntity("E006", "Security Patrol Corp", 750, "surveillance", [36.14, -86.69]),
            
            # Low Stake Entities (100-499 HBAR)
            DroneEntity("E007", "Local Photography Drone", 300, "commercial", [36.11, -86.66]),
            DroneEntity("E008", "Campus Security", 200, "surveillance", [36.12, -86.66]),
            DroneEntity("E009", "Agricultural Survey", 150, "research", [36.10, -86.65]),
            
            # Minimal Stake Entity (< 100 HBAR)
            DroneEntity("E010", "Hobby Drone Pilot", 50, "recreational", [36.13, -86.67])
        ]
        
        return entities
    
    def start_api_server(self):
        """Start the API server for simulation"""
        try:
            import subprocess
            self.api_process = subprocess.Popen(
                ["python3", "hedera_flight_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(3)  # Wait for server to start
            return True
        except Exception as e:
            print(f"❌ Failed to start API server: {e}")
            return False
    
    def submit_flight_plan(self, entity, flight_plan):
        """Submit a flight plan and record results"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/flightplan",
                json=flight_plan,
                timeout=10
            )
            end_time = time.time()
            
            result = {
                "entity": entity.name,
                "entity_id": entity.entity_id,
                "stake": entity.stake_amount,
                "ftc_balance": entity.ftc_balance,
                "flight_id": flight_plan["droneId"],
                "flight_type": flight_plan["flight_type"],
                "priority": flight_plan["priority"],
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                result["status"] = response_data.get("status", "UNKNOWN")
                result["message"] = response_data.get("message", "")
                
                if "APPROVED" in result["status"] or "SUBMITTED" in result["status"]:
                    entity.flight_plans_approved += 1
                    result["outcome"] = "APPROVED"
                else:
                    entity.flight_plans_denied += 1
                    result["outcome"] = "DENIED"
            else:
                entity.flight_plans_denied += 1
                result["outcome"] = "ERROR"
                result["error"] = response.text
            
            self.simulation_results.append(result)
            return result
            
        except Exception as e:
            error_result = {
                "entity": entity.name,
                "entity_id": entity.entity_id,
                "flight_id": flight_plan["droneId"],
                "outcome": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            entity.flight_plans_denied += 1
            self.simulation_results.append(error_result)
            return error_result
    
    def simulate_concurrent_submissions(self, num_rounds=3):
        """Simulate multiple rounds of concurrent flight plan submissions"""
        print("🚁 Starting Multi-Entity Drone Consensus Simulation")
        print("=" * 60)
        print(f"📊 Simulating {len(self.entities)} entities across {num_rounds} rounds")
        print()
        
        for round_num in range(1, num_rounds + 1):
            print(f"🔄 ROUND {round_num} - Concurrent Flight Plan Submissions")
            print("-" * 50)
            
            # Generate flight plans for all entities
            flight_plans = []
            for entity in self.entities:
                if entity.can_submit_flight():
                    flight_type = self.get_flight_type_for_entity(entity)
                    flight_plan = entity.generate_flight_plan(flight_type)
                    flight_plans.append((entity, flight_plan))
            
            # Submit flight plans concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for entity, flight_plan in flight_plans:
                    future = executor.submit(self.submit_flight_plan, entity, flight_plan)
                    futures.append(future)
                
                # Wait for all submissions to complete
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    status_icon = "✅" if result["outcome"] == "APPROVED" else "❌"
                    print(f"{status_icon} {result['entity']} ({result['stake']} HBAR stake) - {result['outcome']}")
            
            print(f"📊 Round {round_num} completed")
            print()
            time.sleep(2)  # Brief pause between rounds
    
    def get_flight_type_for_entity(self, entity):
        """Get appropriate flight type for entity"""
        type_mapping = {
            "commercial": ["delivery", "commercial", "standard"],
            "research": ["research", "surveillance"],
            "emergency_services": ["emergency", "surveillance"],
            "surveillance": ["surveillance", "standard"],
            "recreational": ["standard"]
        }
        
        available_types = type_mapping.get(entity.entity_type, ["standard"])
        return random.choice(available_types)
    
    def simulate_conflict_scenarios(self):
        """Simulate specific conflict scenarios"""
        print("⚠️ CONFLICT SCENARIO SIMULATION")
        print("-" * 40)
        
        # Create overlapping flight plans
        base_time = datetime.now() + timedelta(minutes=10)
        
        # High-stake entity submits first
        high_stake_entity = self.entities[0]  # Amazon
        flight_plan_1 = {
            "droneId": f"{high_stake_entity.entity_id}_conflict_1",
            "start": base_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": (base_time + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "path": [[36.12, -86.67], [36.15, -86.70]],
            "entity": high_stake_entity.name,
            "stake": high_stake_entity.stake_amount,
            "flight_type": "commercial",
            "priority": "HIGH"
        }
        
        # Low-stake entity submits conflicting plan
        low_stake_entity = self.entities[-1]  # Hobby pilot
        flight_plan_2 = {
            "droneId": f"{low_stake_entity.entity_id}_conflict_2",
            "start": (base_time + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": (base_time + timedelta(minutes=45)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "path": [[36.13, -86.68], [36.16, -86.71]],
            "entity": low_stake_entity.name,
            "stake": low_stake_entity.stake_amount,
            "flight_type": "recreational",
            "priority": "LOW"
        }
        
        print(f"📡 {high_stake_entity.name} (Stake: {high_stake_entity.stake_amount} HBAR) submits flight plan")
        result_1 = self.submit_flight_plan(high_stake_entity, flight_plan_1)
        print(f"   Result: {result_1['outcome']}")
        
        print(f"📡 {low_stake_entity.name} (Stake: {low_stake_entity.stake_amount} HBAR) submits conflicting plan")
        result_2 = self.submit_flight_plan(low_stake_entity, flight_plan_2)
        print(f"   Result: {result_2['outcome']}")
        
        if result_1['outcome'] == 'APPROVED' and result_2['outcome'] == 'DENIED':
            print("✅ Conflict resolution working correctly!")
        else:
            print("⚠️ Conflict resolution may need attention")
        
        print()
    
    def generate_simulation_report(self):
        """Generate comprehensive simulation report"""
        total_submissions = len(self.simulation_results)
        approved = len([r for r in self.simulation_results if r.get("outcome") == "APPROVED"])
        denied = len([r for r in self.simulation_results if r.get("outcome") == "DENIED"])
        
        report = f"""
🚁 MULTI-ENTITY DRONE CONSENSUS SIMULATION REPORT
=================================================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 SIMULATION SUMMARY
====================
Total Entities: {len(self.entities)}
Total Submissions: {total_submissions}
Approved: {approved} ✅
Denied: {denied} ❌
Success Rate: {(approved/total_submissions*100):.1f}% if total_submissions > 0 else 0

🏢 ENTITY PERFORMANCE
=====================
"""
        
        for entity in self.entities:
            entity_submissions = [r for r in self.simulation_results if r.get("entity_id") == entity.entity_id]
            entity_approved = len([r for r in entity_submissions if r.get("outcome") == "APPROVED"])
            entity_total = len(entity_submissions)
            
            report += f"""
{entity.name} (ID: {entity.entity_id})
  Stake: {entity.stake_amount} HBAR
  FTC Balance: {entity.ftc_balance}
  Submissions: {entity_total}
  Approved: {entity_approved}
  Success Rate: {(entity_approved/entity_total*100):.1f}% if entity_total > 0 else 0
  Entity Type: {entity.entity_type}
"""
        
        report += f"""
📈 ECONOMIC MODEL ANALYSIS
=========================
High Stake Entities (1000+ HBAR): {len([e for e in self.entities if e.stake_amount >= 1000])}
Medium Stake Entities (500-999 HBAR): {len([e for e in self.entities if e.stake_amount >= 500 and e.stake_amount < 1000])}
Low Stake Entities (100-499 HBAR): {len([e for e in self.entities if e.stake_amount >= 100 and e.stake_amount < 500])}
Minimal Stake Entities (< 100 HBAR): {len([e for e in self.entities if e.stake_amount < 100])}

🎯 KEY INSIGHTS
===============
"""
        
        if approved > denied:
            report += "✅ System favors flight plan approvals\n"
        else:
            report += "⚠️ System shows high denial rate - may indicate conflict detection working\n"
        
        high_stake_entities = [e for e in self.entities if e.stake_amount >= 1000]
        if high_stake_entities:
            high_stake_approved = sum([e.flight_plans_approved for e in high_stake_entities])
            high_stake_total = sum([e.flight_plans_submitted for e in high_stake_entities])
            if high_stake_total > 0:
                report += f"💰 High-stake entities have {(high_stake_approved/high_stake_total*100):.1f}% approval rate\n"
        
        report += f"""
🔗 NEXT STEPS
=============
1. Analyze conflict patterns in denied submissions
2. Optimize FTC token economy based on stake levels
3. Implement priority-based consensus for high-stake entities
4. Scale system for production deployment

---
Simulation completed successfully! 🚁✈️
"""
        
        return report
    
    def cleanup(self):
        """Cleanup simulation environment"""
        if self.api_process:
            self.api_process.terminate()
            self.api_process.wait()
    
    def run_simulation(self):
        """Run complete multi-entity simulation"""
        print("🚀 Starting Multi-Entity Drone Consensus Simulation")
        print("=" * 60)
        
        # Start API server
        if not self.start_api_server():
            print("❌ Cannot start API server. Exiting.")
            return
        
        try:
            # Display entity information
            print("🏢 SIMULATION ENTITIES")
            print("-" * 30)
            for entity in self.entities:
                print(f"{entity.name}: {entity.stake_amount} HBAR stake, {entity.ftc_balance} FTC")
            print()
            
            # Run concurrent submissions
            self.simulate_concurrent_submissions(3)
            
            # Run conflict scenarios
            self.simulate_conflict_scenarios()
            
            # Generate and display report
            report = self.generate_simulation_report()
            print(report)
            
            # Save report to file
            with open("multi_entity_simulation_report.txt", "w") as f:
                f.write(report)
            
            print("📄 Full simulation report saved to: multi_entity_simulation_report.txt")
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    simulator = MultiEntitySimulator()
    try:
        simulator.run_simulation()
    except KeyboardInterrupt:
        print("\n⚠️ Simulation interrupted by user")
        simulator.cleanup()
    except Exception as e:
        print(f"\n❌ Simulation failed: {str(e)}")
        simulator.cleanup()
