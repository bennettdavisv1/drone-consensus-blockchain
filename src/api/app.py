from flask import Flask, request, jsonify
from blockchain import Blockchain

app = Flask(__name__)
bc = Blockchain()

@app.route("/flightplan", methods=["POST"])
def submit_flightplan():
    tx = request.json

    if not tx:
        return jsonify({"status": "DENIED", "message": "No flight plan data provided"}), 400

    required_fields = ["droneId", "start", "end", "path"]
    for field in required_fields:
        if field not in tx:
            return jsonify({"status": "DENIED", "message": f"Missing field: {field}"}), 400

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

if __name__ == "__main__":
    app.run(port=8000)
