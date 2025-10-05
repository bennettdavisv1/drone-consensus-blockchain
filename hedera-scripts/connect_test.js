import dotenv from "dotenv";
dotenv.config();
import { Client } from "@hashgraph/sdk";

async function main() {
    try {
        const client = Client.forNetwork({
            "127.0.0.1:50211": "0.0.3"
        }).setMirrorNetwork("127.0.0.1:5600");

        client.setOperator(process.env.OPERATOR_ID, process.env.OPERATOR_KEY);

        console.log("✅ Connected to local Hedera node successfully!");
    } catch (err) {
        console.error("❌ Failed to connect:", err);
    }
}

main();
