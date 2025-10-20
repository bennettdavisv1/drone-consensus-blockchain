import os
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify
from blockchain import Blockchain
import subprocess
import threading
import queue

app = Flask(__name__)
bc = Blockchain()

# Global queue for Hedera flight plan submissions
hedera_queue = queue.Queue()
hedera_results = {}

class HederaFlightManager:
    def __init__(self):
        self.topic_id = os.getenv('FLIGHT_PLAN_TOPIC_ID')
        self.ftc_token_id = os.getenv('FTC_TOKEN_ID')
        self.staker_id = os.getenv('STAKER_ID')
        self.staker_key = os.getenv('STAKER_KEY')
        
    def submit_to_hedera(self, flight_plan):
        """Submit flight plan to Hedera Consensus Service"""
        try:
            # Create temporary script for this submission
            script_content = f'''
import dotenv from "dotenv";
dotenv.config();
import {{
    Client,
    PrivateKey,
    TopicMessageSubmitTransaction,
    TransferTransaction,
    AccountBalanceQuery
}} from "@hashgraph/sdk";

async function main() {{
    const client = Client.forNetwork({{
        "127.0.0.1:50211": "0.0.3"
    }}).setMirrorNetwork("127.0.0.1:5600");

    const operatorKey = PrivateKey.fromStringED25519(process.env.OPERATOR_KEY);
    const stakerKey = PrivateKey.fromStringED25519(process.env.STAKER_KEY);
    const operatorId = process.env.OPERATOR_ID;
    const stakerAccountId = process.env.STAKER_ID;
    const topicId = process.env.FLIGHT_PLAN_TOPIC_ID;
    const ftcTokenId = process.env.FTC_TOKEN_ID;

    client.setOperator(stakerAccountId, stakerKey);

    const flightPlan = {json.dumps(flight_plan)};

    const message = JSON.stringify(flightPlan);
    const submitTx = await new TopicMessageSubmitTransaction()
        .setTopicId(topicId)
        .setMessage(message)
        .execute(client);

    const submitRx = await submitTx.getReceipt(client);
    console.log("SUCCESS:" + submitRx.transactionId.toString());

    const paymentTx = await new TransferTransaction()
        .addTokenTransfer(ftcTokenId, stakerAccountId, -flightPlan.ftcCost)
        .addTokenTransfer(ftcTokenId, operatorId, flightPlan.ftcCost)
        .execute(client);

    await paymentTx.getReceipt(client);
    console.log("PAYMENT_SUCCESS");
}}

main().catch(console.error);
'''
            
            # Write temporary script
            with open('/tmp/submit_temp.js', 'w') as f:
                f.write(script_content)
            
            # Execute the script
            result = subprocess.run(
                ['node', '/tmp/submit_temp.js'],
                cwd='/Users/bendavis36/Desktop/Vanderbilt/Fall 2025/Research/drone-consensus-blockchain/hedera-scripts',
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Extract transaction ID from output
                for line in result.stdout.split('\n'):
                    if line.startswith('SUCCESS:'):
                        tx_id = line.split('SUCCESS:')[1]
                        return True, tx_id
                return True, "Unknown transaction ID"
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)

hedera_manager = HederaFlightManager()

@app.route("/flightplan", methods=["POST"])
def submit_flightplan():
    tx = request.json

    if not tx:
        return jsonify({"status": "DENIED", "message": "No flight plan data provided"}), 400

    required_fields = ["droneId", "start", "end", "path"]
    for field in required_fields:
        if field not in tx:
            return jsonify({"status": "DENIED", "message": f"Missing field: {field}"}), 400

    # Add Hedera-specific fields
    tx["ftcCost"] = 10  # Cost in FTC tokens
    tx["timestamp"] = datetime.now().isoformat()
    tx["submitter"] = hedera_manager.staker_id

    # Try Hedera submission first
    if hedera_manager.topic_id:
        try:
            success, result = hedera_manager.submit_to_hedera(tx)
            if success:
                return jsonify({
                    "status": "SUBMITTED_TO_HEDERA", 
                    "message": f"Flight plan submitted to Hedera Consensus Service. Transaction: {result}",
                    "transaction_id": result,
                    "ftc_cost": tx["ftcCost"]
                }), 200
            else:
                # Fallback to mock blockchain
                print(f"Hedera submission failed: {result}, falling back to mock blockchain")
        except Exception as e:
            print(f"Hedera submission error: {e}, falling back to mock blockchain")

    # Fallback to mock blockchain
    success, message = bc.add_transaction(tx)
    if success:
        return jsonify({"status": "APPROVED", "message": message}), 200
    else:
        return jsonify({"status": "DENIED", "message": message}), 400

@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = []
    for block in bc.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "prev_hash": block.prev_hash,
            "hash": block.hash
        })
    return jsonify(chain_data)

@app.route("/hedera/status", methods=["GET"])
def hedera_status():
    """Check Hedera integration status"""
    return jsonify({
        "hedera_enabled": bool(hedera_manager.topic_id),
        "topic_id": hedera_manager.topic_id,
        "ftc_token_id": hedera_manager.ftc_token_id,
        "staker_id": hedera_manager.staker_id
    })

@app.route("/hedera/consume", methods=["POST"])
def start_hedera_consumer():
    """Start the Hedera message consumer in background"""
    def run_consumer():
        subprocess.run([
            'node', 'consume_flightplans.js'
        ], cwd='/Users/bendavis36/Desktop/Vanderbilt/Fall 2025/Research/drone-consensus-blockchain/hedera-scripts')
    
    thread = threading.Thread(target=run_consumer, daemon=True)
    thread.start()
    
    return jsonify({"status": "Consumer started", "message": "Hedera message consumer is now running in background"})

if __name__ == "__main__":
    print("🚀 Starting Drone Consensus Blockchain API...")
    print("📡 Hedera integration:", "ENABLED" if hedera_manager.topic_id else "DISABLED")
    if hedera_manager.topic_id:
        print(f"   Topic ID: {hedera_manager.topic_id}")
        print(f"   FTC Token: {hedera_manager.ftc_token_id}")
    print("🌐 API running on http://127.0.0.1:8000")
    app.run(port=8000)
