import hashlib, json, time
from datetime import datetime

class Block:
    def __init__(self, index, prev_hash, transactions):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "prev_hash": self.prev_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        # Create the genesis block
        genesis_block = Block(0, "0", [])
        self.chain = [genesis_block]

    def validate_transaction(self, new_tx):
        """Check if the new transaction conflicts with any existing one."""
        try:
            new_start = datetime.fromisoformat(new_tx["start"].replace("Z", ""))
            new_end = datetime.fromisoformat(new_tx["end"].replace("Z", ""))
        except Exception as e:
            return False, f"Invalid date format: {e}"

        for block in self.chain:
            for tx in block.transactions:
                existing_start = datetime.fromisoformat(tx["start"].replace("Z", ""))
                existing_end = datetime.fromisoformat(tx["end"].replace("Z", ""))

                # Simple time overlap rule
                if new_start < existing_end and existing_start < new_end:
                    return False, (
                        f"Conflict with drone {tx['droneId']} "
                        f"from {tx['start']} to {tx['end']}"
                    )

        return True, "No conflict"

    def add_transaction(self, tx):
        """Try adding a transaction, return status and message."""
        ok, msg = self.validate_transaction(tx)
        if not ok:
            return False, msg

        # If valid, commit it in a new block
        new_block = Block(len(self.chain), self.chain[-1].hash, [tx])
        self.chain.append(new_block)
        return True, "Approved"
