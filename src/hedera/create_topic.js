import dotenv from "dotenv";
dotenv.config();
import {
    Client,
    PrivateKey,
    TopicCreateTransaction,
    TopicMessageSubmitTransaction,
    TopicMessageQuery,
    TopicId
} from "@hashgraph/sdk";

async function main() {
    const client = Client.forNetwork({
        "127.0.0.1:50211": "0.0.3"
    }).setMirrorNetwork("127.0.0.1:5600");

    const operatorKey = PrivateKey.fromStringED25519(process.env.OPERATOR_KEY);
    client.setOperator(process.env.OPERATOR_ID, operatorKey);

    console.log("🏗️ Creating HCS topic for flight plan submissions...");

    // Create a new topic for flight plans
    const topicCreateTx = await new TopicCreateTransaction()
        .setTopicMemo("Drone Flight Plan Consensus Topic")
        .execute(client);

    const topicCreateRx = await topicCreateTx.getReceipt(client);
    const topicId = topicCreateRx.topicId;

    console.log(`✅ Flight plan topic created! Topic ID: ${topicId.toString()}`);
    console.log(`📝 Topic Memo: Drone Flight Plan Consensus Topic`);
    console.log(`🔗 Use this Topic ID in your flight plan submissions`);

    // Save topic ID to .env for other scripts
    console.log(`\n💾 Add this to your .env file:`);
    console.log(`FLIGHT_PLAN_TOPIC_ID=${topicId.toString()}`);

    console.log(`\n🎯 Next steps:`);
    console.log(`1. Add FLIGHT_PLAN_TOPIC_ID=${topicId.toString()} to your .env file`);
    console.log(`2. Run: node submit_flightplan.js`);
    console.log(`3. Run: node consume_flightplans.js`);
}

main().catch(console.error);
