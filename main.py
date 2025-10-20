#!/usr/bin/env python3
"""
Drone Consensus Blockchain - Main Entry Point
=============================================

This is the main entry point for the Drone Consensus Blockchain system.
It provides a command-line interface for running the system components.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(
        description="Drone Consensus Blockchain System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py api                    # Start the API server
  python main.py test                   # Run all tests
  python main.py simulate               # Run simulations
  python main.py hedera setup           # Setup Hedera environment
  python main.py hedera submit          # Submit flight plan to Hedera
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Start the API server')
    api_parser.add_argument('--host', default='127.0.0.1', help='API host')
    api_parser.add_argument('--port', type=int, default=8000, help='API port')
    api_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    test_parser.add_argument('--stress', action='store_true', help='Run stress tests')
    
    # Simulate command
    sim_parser = subparsers.add_parser('simulate', help='Run simulations')
    sim_parser.add_argument('--entities', type=int, default=10, help='Number of entities')
    sim_parser.add_argument('--rounds', type=int, default=3, help='Number of simulation rounds')
    
    # Hedera command
    hedera_parser = subparsers.add_parser('hedera', help='Hedera operations')
    hedera_subparsers = hedera_parser.add_subparsers(dest='hedera_command')
    
    hedera_subparsers.add_parser('setup', help='Setup Hedera environment')
    hedera_subparsers.add_parser('submit', help='Submit flight plan to Hedera')
    hedera_subparsers.add_parser('consume', help='Start message consumer')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'api':
        start_api(args)
    elif args.command == 'test':
        run_tests(args)
    elif args.command == 'simulate':
        run_simulation(args)
    elif args.command == 'hedera':
        run_hedera_operations(args)

def start_api(args):
    """Start the API server"""
    print("🚀 Starting Drone Consensus Blockchain API...")
    try:
        from src.api.hedera_flight_api import app
        app.run(host=args.host, port=args.port, debug=args.debug)
    except ImportError:
        print("❌ API module not found. Please check your installation.")
        sys.exit(1)

def run_tests(args):
    """Run tests"""
    print("🧪 Running Drone Consensus Blockchain tests...")
    if args.quick:
        print("Running quick tests...")
        # Run quick tests
    elif args.stress:
        print("Running stress tests...")
        # Run stress tests
    else:
        print("Running all tests...")
        # Run all tests

def run_simulation(args):
    """Run simulations"""
    print(f"🚁 Running simulation with {args.entities} entities for {args.rounds} rounds...")
    # Run simulation logic

def run_hedera_operations(args):
    """Run Hedera operations"""
    if args.hedera_command == 'setup':
        print("🔧 Setting up Hedera environment...")
        # Setup Hedera environment
    elif args.hedera_command == 'submit':
        print("✈️ Submitting flight plan to Hedera...")
        # Submit flight plan
    elif args.hedera_command == 'consume':
        print("📡 Starting Hedera message consumer...")
        # Start message consumer
    else:
        print("❌ Unknown Hedera command")

if __name__ == "__main__":
    main()
