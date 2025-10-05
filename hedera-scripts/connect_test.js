import { Client } from "@hashgraph/sdk";

const client = Client.forNetwork({
    "127.0.0.1:50211": "0.0.3"
}).setMirrorNetwork("127.0.0.1:5600");

console.log("✅ Connected to local Hedera node");
