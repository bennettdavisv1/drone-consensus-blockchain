"""
Configuration settings for Drone Consensus Blockchain
===================================================
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
CONFIG_DIR = PROJECT_ROOT / "config"
TESTS_DIR = PROJECT_ROOT / "tests"
DOCS_DIR = PROJECT_ROOT / "docs"

# API Configuration
API_HOST = "127.0.0.1"
API_PORT = 8000
API_DEBUG = True

# Hedera Configuration
HEDERA_NETWORK = "127.0.0.1:50211"
HEDERA_MIRROR = "127.0.0.1:5600"
HEDERA_NODE_ID = "0.0.3"

# Flight Plan Configuration
DEFAULT_FTC_COST = 10
CONFLICT_DETECTION_ENABLED = True
PRIORITY_BASED_CONSENSUS = True

# Entity Configuration
DEFAULT_ENTITIES = [
    {
        "id": "E001",
        "name": "Amazon Drone Delivery",
        "stake_hbar": 1500,
        "entity_type": "commercial",
        "priority": "HIGH"
    },
    {
        "id": "E002", 
        "name": "Vanderbilt Research Lab",
        "stake_hbar": 1200,
        "entity_type": "research",
        "priority": "HIGH"
    },
    {
        "id": "E003",
        "name": "Nashville Emergency Services",
        "stake_hbar": 2000,
        "entity_type": "emergency",
        "priority": "CRITICAL"
    }
]

# Testing Configuration
TEST_TIMEOUT = 30
SIMULATION_ROUNDS = 3
STRESS_TEST_USERS = 10
STRESS_TEST_SUBMISSIONS = 50

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
