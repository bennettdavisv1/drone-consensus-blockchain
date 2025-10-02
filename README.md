
# Drone Consensus Blockchain (Mock Implementation)

This project provides a **mock blockchain** system for submitting drone flight plans and reaching consensus on whether they can be approved.  
It validates each plan against existing approved flights to prevent **conflicts** (overlapping times).  

This is a lightweight prototype — no tokens, no gas, no real blockchain required.  
It can later be extended to Hedera Hashgraph or another distributed ledger.

---

## Features
- Submit flight plans as JSON via a REST API
- Approves non-conflicting flights, rejects overlapping ones
- Maintains a blockchain ledger of approved flight plans
- Returns clear responses: **APPROVED** or **DENIED**
- Exposes chain history for auditing

---

## Setup

### 1. Clone the Repo
```bash
git clone <repo-url>
cd drone-consensus-blockchain
````

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows PowerShell
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Server

```bash
python app.py
```

Server runs at:

```
http://127.0.0.1:8000
```

---

## API Endpoints

### Submit Flight Plan

```bash
curl -X POST http://127.0.0.1:8000/flightplan \
  -H "Content-Type: application/json" \
  -d '{
        "droneId": "drone123",
        "start": "2025-10-02T14:00:00Z",
        "end": "2025-10-02T14:30:00Z",
        "path": [[36.12, -86.67], [36.15, -86.70]]
      }'
```

**Response (Approved):**

```json
{"status": "APPROVED", "message": "Approved"}
```

**Response (Denied):**

```json
{"status": "DENIED", "message": "Conflict with drone drone123 from 2025-10-02T14:00:00Z to 2025-10-02T14:30:00Z"}
```

---

### Get Blockchain Ledger

```bash
curl http://127.0.0.1:8000/chain
```

Returns a full JSON list of blocks and transactions.
```
