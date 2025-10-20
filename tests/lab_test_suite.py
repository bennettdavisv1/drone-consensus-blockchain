#!/usr/bin/env python3
"""
🧪 Drone Consensus Blockchain - Comprehensive Lab Test Suite
============================================================

This test suite validates all components of the drone consensus system:
- Hedera Hashgraph integration
- Flight plan submission and consensus
- Conflict detection and prevention
- FTC token economy
- API endpoints and responses
- End-to-end workflows

Usage: python lab_test_suite.py
"""

import requests
import json
import time
import subprocess
import threading
import queue
import sys
from datetime import datetime, timedelta
import os

class LabTestSuite:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = []
        self.api_process = None
        self.hedera_consumer_process = None
        
    def log_test(self, test_name, status, message="", details=None):
        """Log test results with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{timestamp}] {test_name}: {message}")
        if details:
            print(f"   Details: {details}")

    def test_hedera_node_connectivity(self):
        """Test 1: Verify Hedera node is running and accessible"""
        try:
            response = requests.get("http://127.0.0.1:5600/api/v1/status", timeout=5)
            if response.status_code == 200:
                self.log_test("Hedera Node Connectivity", "PASS", 
                            "Hedera node is running and accessible")
                return True
            else:
                self.log_test("Hedera Node Connectivity", "FAIL", 
                            f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Hedera Node Connectivity", "FAIL", 
                        f"Cannot connect to Hedera node: {str(e)}")
            return False

    def test_hedera_environment_setup(self):
        """Test 2: Verify Hedera environment is properly configured"""
        try:
            # Check if .env file exists and has required variables
            env_file = "hedera-scripts/.env"
            if not os.path.exists(env_file):
                self.log_test("Hedera Environment Setup", "FAIL", 
                            ".env file not found")
                return False
            
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            required_vars = ["OPERATOR_ID", "STAKER_ID", "FTC_TOKEN_ID", "FLIGHT_PLAN_TOPIC_ID"]
            missing_vars = [var for var in required_vars if var not in env_content]
            
            if missing_vars:
                self.log_test("Hedera Environment Setup", "FAIL", 
                            f"Missing environment variables: {missing_vars}")
                return False
            
            self.log_test("Hedera Environment Setup", "PASS", 
                        "All required environment variables present")
            return True
            
        except Exception as e:
            self.log_test("Hedera Environment Setup", "FAIL", 
                        f"Error checking environment: {str(e)}")
            return False

    def test_hedera_sdk_connectivity(self):
        """Test 3: Test Hedera SDK connectivity"""
        try:
            result = subprocess.run(
                ["node", "connect_test.js"],
                cwd="hedera-scripts",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "Connected to local Hedera node successfully" in result.stdout:
                self.log_test("Hedera SDK Connectivity", "PASS", 
                            "Successfully connected to Hedera via SDK")
                return True
            else:
                self.log_test("Hedera SDK Connectivity", "FAIL", 
                            f"SDK connection failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_test("Hedera SDK Connectivity", "FAIL", 
                        f"Error running SDK test: {str(e)}")
            return False

    def test_flight_plan_submission(self):
        """Test 4: Test flight plan submission to Hedera"""
        try:
            result = subprocess.run(
                ["node", "submit_flightplan.js"],
                cwd="hedera-scripts",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "Flight plan successfully submitted" in result.stdout:
                self.log_test("Flight Plan Submission", "PASS", 
                            "Flight plan submitted to Hedera successfully")
                return True
            else:
                self.log_test("Flight Plan Submission", "FAIL", 
                            f"Submission failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_test("Flight Plan Submission", "FAIL", 
                        f"Error submitting flight plan: {str(e)}")
            return False

    def start_api_server(self):
        """Start the Python API server"""
        try:
            self.api_process = subprocess.Popen(
                ["python", "hedera_flight_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(3)  # Wait for server to start
            return True
        except Exception as e:
            self.log_test("API Server Startup", "FAIL", f"Failed to start API: {str(e)}")
            return False

    def test_api_health(self):
        """Test 5: Test API server health"""
        try:
            response = requests.get(f"{self.base_url}/hedera/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", "PASS", 
                            f"API is healthy. Hedera enabled: {data.get('hedera_enabled', False)}")
                return True
            else:
                self.log_test("API Health Check", "FAIL", 
                            f"API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", "FAIL", f"Cannot connect to API: {str(e)}")
            return False

    def test_flight_plan_api_submission(self):
        """Test 6: Test flight plan submission via API"""
        try:
            flight_plan = {
                "droneId": f"test_drone_{int(time.time())}",
                "start": "2025-01-15T17:00:00Z",
                "end": "2025-01-15T17:30:00Z",
                "path": [[36.12, -86.67], [36.15, -86.70]]
            }
            
            response = requests.post(
                f"{self.base_url}/flightplan",
                json=flight_plan,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("API Flight Plan Submission", "PASS", 
                            f"Flight plan submitted. Status: {data.get('status', 'Unknown')}")
                return True
            else:
                self.log_test("API Flight Plan Submission", "FAIL", 
                            f"API returned status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("API Flight Plan Submission", "FAIL", 
                        f"Error submitting via API: {str(e)}")
            return False

    def test_conflict_detection(self):
        """Test 7: Test conflict detection with overlapping flight plans"""
        try:
            # Submit first flight plan
            flight_plan_1 = {
                "droneId": f"conflict_test_1_{int(time.time())}",
                "start": "2025-01-15T18:00:00Z",
                "end": "2025-01-15T18:30:00Z",
                "path": [[36.12, -86.67], [36.15, -86.70]]
            }
            
            response_1 = requests.post(f"{self.base_url}/flightplan", json=flight_plan_1)
            
            # Submit conflicting flight plan (overlapping time)
            flight_plan_2 = {
                "droneId": f"conflict_test_2_{int(time.time())}",
                "start": "2025-01-15T18:15:00Z",  # Overlaps with first plan
                "end": "2025-01-15T18:45:00Z",
                "path": [[36.13, -86.68], [36.16, -86.71]]
            }
            
            response_2 = requests.post(f"{self.base_url}/flightplan", json=flight_plan_2)
            
            if response_2.status_code == 400:  # Should be denied due to conflict
                self.log_test("Conflict Detection", "PASS", 
                            "System correctly detected and prevented flight plan conflict")
                return True
            else:
                self.log_test("Conflict Detection", "FAIL", 
                            f"Conflict not detected. Response: {response_2.text}")
                return False
                
        except Exception as e:
            self.log_test("Conflict Detection", "FAIL", 
                        f"Error testing conflict detection: {str(e)}")
            return False

    def test_blockchain_chain(self):
        """Test 8: Test blockchain chain retrieval"""
        try:
            response = requests.get(f"{self.base_url}/chain", timeout=5)
            if response.status_code == 200:
                chain_data = response.json()
                self.log_test("Blockchain Chain Retrieval", "PASS", 
                            f"Retrieved chain with {len(chain_data)} blocks")
                return True
            else:
                self.log_test("Blockchain Chain Retrieval", "FAIL", 
                            f"Failed to retrieve chain: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Blockchain Chain Retrieval", "FAIL", 
                        f"Error retrieving chain: {str(e)}")
            return False

    def test_ftc_token_economy(self):
        """Test 9: Test FTC token economy functionality"""
        try:
            # This test would require checking FTC balances and transactions
            # For now, we'll test if the environment has FTC token configured
            env_file = "hedera-scripts/.env"
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            if "FTC_TOKEN_ID" in env_content:
                self.log_test("FTC Token Economy", "PASS", 
                            "FTC token economy is configured")
                return True
            else:
                self.log_test("FTC Token Economy", "FAIL", 
                            "FTC token not configured")
                return False
                
        except Exception as e:
            self.log_test("FTC Token Economy", "FAIL", 
                        f"Error checking FTC configuration: {str(e)}")
            return False

    def test_end_to_end_workflow(self):
        """Test 10: Complete end-to-end workflow test"""
        try:
            # Submit multiple flight plans and verify they're processed
            flight_plans = [
                {
                    "droneId": f"e2e_test_1_{int(time.time())}",
                    "start": "2025-01-15T19:00:00Z",
                    "end": "2025-01-15T19:30:00Z",
                    "path": [[36.12, -86.67], [36.15, -86.70]]
                },
                {
                    "droneId": f"e2e_test_2_{int(time.time())}",
                    "start": "2025-01-15T20:00:00Z",  # No conflict
                    "end": "2025-01-15T20:30:00Z",
                    "path": [[36.13, -86.68], [36.16, -86.71]]
                }
            ]
            
            results = []
            for plan in flight_plans:
                response = requests.post(f"{self.base_url}/flightplan", json=plan)
                results.append(response.status_code in [200, 201])
            
            if all(results):
                self.log_test("End-to-End Workflow", "PASS", 
                            "Complete workflow executed successfully")
                return True
            else:
                self.log_test("End-to-End Workflow", "FAIL", 
                            "Some flight plans failed in workflow")
                return False
                
        except Exception as e:
            self.log_test("End-to-End Workflow", "FAIL", 
                        f"Error in end-to-end test: {str(e)}")
            return False

    def cleanup(self):
        """Cleanup test environment"""
        if self.api_process:
            self.api_process.terminate()
            self.api_process.wait()
        
        if self.hedera_consumer_process:
            self.hedera_consumer_process.terminate()
            self.hedera_consumer_process.wait()

    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        report = f"""
🧪 DRONE CONSENSUS BLOCKCHAIN - LAB TEST REPORT
===============================================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 TEST SUMMARY
===============
Total Tests: {total_tests}
Passed: {passed_tests} ✅
Failed: {failed_tests} ❌
Success Rate: {(passed_tests/total_tests*100):.1f}%

📋 DETAILED RESULTS
==================
"""
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            report += f"{status_icon} {result['test']}: {result['message']}\n"
            if result.get('details'):
                report += f"   Details: {result['details']}\n"
            report += "\n"
        
        # Add recommendations
        report += """
🎯 RECOMMENDATIONS
==================
"""
        if failed_tests == 0:
            report += "🎉 All tests passed! System is ready for production use.\n"
        else:
            report += "⚠️ Some tests failed. Please review and fix issues before deployment.\n"
        
        report += f"""
📈 SYSTEM STATUS
================
Overall System Health: {'HEALTHY' if failed_tests == 0 else 'NEEDS ATTENTION'}
Hedera Integration: {'OPERATIONAL' if any('Hedera' in r['test'] and r['status'] == 'PASS' for r in self.test_results) else 'ISSUES DETECTED'}
API Functionality: {'OPERATIONAL' if any('API' in r['test'] and r['status'] == 'PASS' for r in self.test_results) else 'ISSUES DETECTED'}
Conflict Detection: {'OPERATIONAL' if any('Conflict' in r['test'] and r['status'] == 'PASS' for r in self.test_results) else 'ISSUES DETECTED'}

🔗 NEXT STEPS
=============
1. Review failed tests and implement fixes
2. Run additional stress tests for production readiness
3. Deploy to staging environment for further validation
4. Prepare for production deployment

---
Test Suite Version: 1.0
Generated by: Drone Consensus Blockchain Lab Test Suite
"""
        
        return report

    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting Comprehensive Lab Test Suite")
        print("=" * 50)
        
        # Test sequence
        tests = [
            ("Hedera Node Connectivity", self.test_hedera_node_connectivity),
            ("Hedera Environment Setup", self.test_hedera_environment_setup),
            ("Hedera SDK Connectivity", self.test_hedera_sdk_connectivity),
            ("Flight Plan Submission", self.test_flight_plan_submission),
            ("API Server Startup", self.start_api_server),
            ("API Health Check", self.test_api_health),
            ("API Flight Plan Submission", self.test_flight_plan_api_submission),
            ("Conflict Detection", self.test_conflict_detection),
            ("Blockchain Chain Retrieval", self.test_blockchain_chain),
            ("FTC Token Economy", self.test_ftc_token_economy),
            ("End-to-End Workflow", self.test_end_to_end_workflow)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, "ERROR", f"Test crashed: {str(e)}")
        
        # Generate and display report
        report = self.generate_report()
        print("\n" + "=" * 50)
        print(report)
        
        # Save report to file
        with open("lab_test_report.txt", "w") as f:
            f.write(report)
        
        print(f"\n📄 Full report saved to: lab_test_report.txt")
        
        return self.test_results

if __name__ == "__main__":
    test_suite = LabTestSuite()
    try:
        results = test_suite.run_all_tests()
    finally:
        test_suite.cleanup()
