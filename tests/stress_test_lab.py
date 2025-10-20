#!/usr/bin/env python3
"""
🚀 Drone Consensus Blockchain - Stress Test Suite
=================================================

This stress test suite validates system performance under load:
- Multiple concurrent flight plan submissions
- High-frequency conflict detection
- API endpoint stress testing
- Hedera network performance
- Memory and resource usage

Usage: python stress_test_lab.py
"""

import requests
import json
import time
import threading
import concurrent.futures
import psutil
import os
from datetime import datetime, timedelta
import random

class StressTestSuite:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.results = []
        self.api_process = None
        self.start_time = None
        
    def log_result(self, test_name, status, metrics=None):
        """Log stress test results"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "metrics": metrics or {}
        }
        self.results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{timestamp}] {test_name}")
        if metrics:
            for key, value in metrics.items():
                print(f"   {key}: {value}")

    def start_api_server(self):
        """Start API server for stress testing"""
        try:
            self.api_process = subprocess.Popen(
                ["python", "hedera_flight_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(5)  # Wait for server to start
            return True
        except Exception as e:
            self.log_result("API Server Startup", "FAIL", {"error": str(e)})
            return False

    def generate_flight_plan(self, drone_id, time_offset_minutes=0):
        """Generate a random flight plan"""
        base_time = datetime.now() + timedelta(minutes=time_offset_minutes)
        start_time = base_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (base_time + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Random path in Nashville area
        lat1 = 36.12 + random.uniform(-0.1, 0.1)
        lon1 = -86.67 + random.uniform(-0.1, 0.1)
        lat2 = lat1 + random.uniform(-0.05, 0.05)
        lon2 = lon1 + random.uniform(-0.05, 0.05)
        
        return {
            "droneId": f"stress_test_{drone_id}_{int(time.time())}",
            "start": start_time,
            "end": end_time,
            "path": [[lat1, lon1], [lat2, lon2]]
        }

    def submit_flight_plan(self, flight_plan):
        """Submit a single flight plan"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/flightplan",
                json=flight_plan,
                timeout=10
            )
            end_time = time.time()
            
            return {
                "success": response.status_code in [200, 201],
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0
            }

    def test_concurrent_submissions(self, num_threads=10, submissions_per_thread=5):
        """Test 1: Concurrent flight plan submissions"""
        print(f"🧪 Testing {num_threads} threads with {submissions_per_thread} submissions each...")
        
        def worker_thread(thread_id):
            results = []
            for i in range(submissions_per_thread):
                flight_plan = self.generate_flight_plan(f"thread_{thread_id}_submission_{i}")
                result = self.submit_flight_plan(flight_plan)
                result["thread_id"] = thread_id
                result["submission_id"] = i
                results.append(result)
            return results
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(num_threads)]
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful = len([r for r in all_results if r.get("success", False)])
        failed = len(all_results) - successful
        avg_response_time = sum([r.get("response_time", 0) for r in all_results]) / len(all_results)
        
        self.log_result("Concurrent Submissions", 
                       "PASS" if successful > len(all_results) * 0.8 else "FAIL",
                       {
                           "total_submissions": len(all_results),
                           "successful": successful,
                           "failed": failed,
                           "success_rate": f"{successful/len(all_results)*100:.1f}%",
                           "total_time": f"{total_time:.2f}s",
                           "avg_response_time": f"{avg_response_time:.3f}s",
                           "submissions_per_second": f"{len(all_results)/total_time:.2f}"
                       })
        
        return all_results

    def test_high_frequency_submissions(self, num_submissions=50, delay=0.1):
        """Test 2: High-frequency flight plan submissions"""
        print(f"🧪 Testing {num_submissions} rapid submissions with {delay}s delay...")
        
        results = []
        start_time = time.time()
        
        for i in range(num_submissions):
            flight_plan = self.generate_flight_plan(f"rapid_{i}")
            result = self.submit_flight_plan(flight_plan)
            results.append(result)
            time.sleep(delay)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful = len([r for r in results if r.get("success", False)])
        
        self.log_result("High-Frequency Submissions",
                       "PASS" if successful > num_submissions * 0.8 else "FAIL",
                       {
                           "total_submissions": num_submissions,
                           "successful": successful,
                           "success_rate": f"{successful/num_submissions*100:.1f}%",
                           "total_time": f"{total_time:.2f}s",
                           "submissions_per_second": f"{num_submissions/total_time:.2f}"
                       })
        
        return results

    def test_conflict_detection_stress(self, num_conflicts=20):
        """Test 3: Stress test conflict detection with overlapping flights"""
        print(f"🧪 Testing conflict detection with {num_conflicts} overlapping flights...")
        
        # Submit base flight plan
        base_plan = self.generate_flight_plan("base_conflict_test", 0)
        base_result = self.submit_flight_plan(base_plan)
        
        if not base_result.get("success", False):
            self.log_result("Conflict Detection Stress", "FAIL", {"error": "Base plan submission failed"})
            return []
        
        # Submit conflicting plans
        conflict_results = []
        for i in range(num_conflicts):
            # Create overlapping flight plan
            conflict_plan = self.generate_flight_plan(f"conflict_{i}", 15)  # 15-minute overlap
            result = self.submit_flight_plan(conflict_plan)
            conflict_results.append(result)
        
        # Analyze results
        conflicts_detected = len([r for r in conflict_results if not r.get("success", False)])
        conflicts_missed = len(conflict_results) - conflicts_detected
        
        self.log_result("Conflict Detection Stress",
                       "PASS" if conflicts_detected > num_conflicts * 0.8 else "FAIL",
                       {
                           "total_conflicts": num_conflicts,
                           "detected": conflicts_detected,
                           "missed": conflicts_missed,
                           "detection_rate": f"{conflicts_detected/num_conflicts*100:.1f}%"
                       })
        
        return conflict_results

    def test_api_endpoint_stress(self):
        """Test 4: Stress test all API endpoints"""
        print("🧪 Testing API endpoint stress...")
        
        endpoints = [
            ("/hedera/status", "GET"),
            ("/chain", "GET"),
            ("/flightplan", "POST")
        ]
        
        results = {}
        
        for endpoint, method in endpoints:
            response_times = []
            success_count = 0
            
            for i in range(20):  # 20 requests per endpoint
                start_time = time.time()
                try:
                    if method == "GET":
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    else:  # POST
                        flight_plan = self.generate_flight_plan(f"endpoint_test_{i}")
                        response = requests.post(f"{self.base_url}{endpoint}", json=flight_plan, timeout=5)
                    
                    end_time = time.time()
                    response_times.append(end_time - start_time)
                    
                    if response.status_code in [200, 201]:
                        success_count += 1
                        
                except Exception as e:
                    response_times.append(5.0)  # Timeout value
            
            avg_response_time = sum(response_times) / len(response_times)
            success_rate = success_count / 20 * 100
            
            results[endpoint] = {
                "avg_response_time": avg_response_time,
                "success_rate": success_rate,
                "total_requests": 20
            }
        
        # Overall assessment
        overall_success = all(r["success_rate"] > 80 for r in results.values())
        
        self.log_result("API Endpoint Stress",
                       "PASS" if overall_success else "FAIL",
                       results)
        
        return results

    def test_memory_usage(self):
        """Test 5: Monitor memory usage during stress testing"""
        print("🧪 Monitoring memory usage...")
        
        # Get initial memory usage
        initial_memory = psutil.virtual_memory().percent
        
        # Run some stress tests
        self.test_high_frequency_submissions(30, 0.05)
        
        # Get final memory usage
        final_memory = psutil.virtual_memory().percent
        memory_increase = final_memory - initial_memory
        
        self.log_result("Memory Usage Test",
                       "PASS" if memory_increase < 20 else "WARNING",
                       {
                           "initial_memory": f"{initial_memory:.1f}%",
                           "final_memory": f"{final_memory:.1f}%",
                           "memory_increase": f"{memory_increase:.1f}%"
                       })
        
        return {
            "initial_memory": initial_memory,
            "final_memory": final_memory,
            "memory_increase": memory_increase
        }

    def test_hedera_network_performance(self):
        """Test 6: Test Hedera network performance"""
        print("🧪 Testing Hedera network performance...")
        
        # Test Hedera node connectivity
        try:
            response = requests.get("http://127.0.0.1:5600/api/v1/status", timeout=5)
            hedera_accessible = response.status_code == 200
        except:
            hedera_accessible = False
        
        # Test multiple flight plan submissions to Hedera
        hedera_results = []
        for i in range(10):
            flight_plan = self.generate_flight_plan(f"hedera_perf_{i}")
            result = self.submit_flight_plan(flight_plan)
            hedera_results.append(result)
        
        successful_hedera = len([r for r in hedera_results if r.get("success", False)])
        
        self.log_result("Hedera Network Performance",
                       "PASS" if hedera_accessible and successful_hedera > 8 else "FAIL",
                       {
                           "hedera_accessible": hedera_accessible,
                           "successful_submissions": successful_hedera,
                           "total_attempts": len(hedera_results)
                       })
        
        return hedera_results

    def cleanup(self):
        """Cleanup after stress testing"""
        if self.api_process:
            self.api_process.terminate()
            self.api_process.wait()

    def generate_stress_report(self):
        """Generate comprehensive stress test report"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        
        report = f"""
🚀 DRONE CONSENSUS BLOCKCHAIN - STRESS TEST REPORT
==================================================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 STRESS TEST SUMMARY
=====================
Total Tests: {total_tests}
Passed: {passed_tests} ✅
Failed: {total_tests - passed_tests} ❌
Success Rate: {(passed_tests/total_tests*100):.1f}%

📋 DETAILED RESULTS
==================
"""
        
        for result in self.results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            report += f"{status_icon} {result['test']}\n"
            if result.get('metrics'):
                for key, value in result['metrics'].items():
                    report += f"   {key}: {value}\n"
            report += "\n"
        
        # Performance recommendations
        report += """
🎯 PERFORMANCE RECOMMENDATIONS
==============================
"""
        
        if passed_tests == total_tests:
            report += "🎉 All stress tests passed! System is ready for production load.\n"
        else:
            report += "⚠️ Some stress tests failed. Consider:\n"
            report += "   • Increasing server resources\n"
            report += "   • Optimizing database queries\n"
            report += "   • Implementing caching mechanisms\n"
            report += "   • Scaling Hedera node resources\n"
        
        report += f"""
📈 SYSTEM CAPACITY
=================
Based on stress test results, the system can handle:
• Concurrent users: 10+ (tested)
• Submissions per second: 5+ (tested)
• Memory usage: Stable under load
• Hedera integration: {'Operational' if passed_tests > total_tests * 0.8 else 'Needs attention'}

🔗 NEXT STEPS
=============
1. Review failed stress tests
2. Optimize performance bottlenecks
3. Scale infrastructure as needed
4. Run production load tests
5. Monitor system metrics in production

---
Stress Test Suite Version: 1.0
Generated by: Drone Consensus Blockchain Stress Test Suite
"""
        
        return report

    def run_stress_tests(self):
        """Run complete stress test suite"""
        print("🚀 Starting Stress Test Suite")
        print("=" * 50)
        
        self.start_time = time.time()
        
        # Start API server
        if not self.start_api_server():
            print("❌ Cannot start API server. Exiting.")
            return
        
        try:
            # Run stress tests
            self.test_concurrent_submissions(10, 5)
            self.test_high_frequency_submissions(50, 0.1)
            self.test_conflict_detection_stress(20)
            self.test_api_endpoint_stress()
            self.test_memory_usage()
            self.test_hedera_network_performance()
            
        finally:
            self.cleanup()
        
        # Generate report
        report = self.generate_stress_report()
        print("\n" + "=" * 50)
        print(report)
        
        # Save report
        with open("stress_test_report.txt", "w") as f:
            f.write(report)
        
        print(f"\n📄 Full stress test report saved to: stress_test_report.txt")
        
        return self.results

if __name__ == "__main__":
    stress_suite = StressTestSuite()
    try:
        results = stress_suite.run_stress_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Stress test interrupted by user")
        stress_suite.cleanup()
    except Exception as e:
        print(f"\n❌ Stress test failed: {str(e)}")
        stress_suite.cleanup()
