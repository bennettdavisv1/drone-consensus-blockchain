import dotenv from "dotenv";
dotenv.config();
import {
    Client,
    PrivateKey,
    TopicMessageSubmitTransaction,
    TransferTransaction,
    AccountBalanceQuery
} from "@hashgraph/sdk";

async function main() {
    const client = Client.forNetwork({
        "127.0.0.1:50211": "0.0.3"
    }).setMirrorNetwork("127.0.0.1:5600");

    const operatorKey = PrivateKey.fromStringED25519(process.env.OPERATOR_KEY);
    const stakerKey = PrivateKey.fromStringED25519(process.env.STAKER_KEY);
    const operatorId = process.env.OPERATOR_ID;
    const stakerAccountId = process.env.STAKER_ID;
    const topicId = process.env.FLIGHT_PLAN_TOPIC_ID;
    const ftcTokenId = process.env.FTC_TOKEN_ID;

    if (!topicId) {
        console.error("❌ FLIGHT_PLAN_TOPIC_ID not found in .env file");
        console.log("💡 Run: node create_topic.js first");
        return;
    }

    if (!ftcTokenId) {
        console.error("❌ FTC_TOKEN_ID not found in .env file");
        console.log("💡 Run: node mint_ftc.js first");
        return;
    }

    client.setOperator(stakerAccountId, stakerKey);

    // Check FTC balance
    const balance = await new AccountBalanceQuery()
        .setAccountId(stakerAccountId)
        .execute(client);

    const ftcBalance = balance.tokens._map.get(ftcTokenId) || 0;
    console.log(`💰 Current FTC balance: ${ftcBalance}`);

    if (ftcBalance < 10) {
        console.error("❌ Insufficient FTC balance. Need at least 10 FTC to submit flight plan.");
        return;
    }

    // Create flight plan data
    const flightPlan = {
        droneId: "drone_" + Date.now(),
        start: "2025-01-15T14:00:00Z",
        end: "2025-01-15T14:30:00Z",
        path: [
            [36.12, -86.67], // Nashville coordinates
            [36.15, -86.70]
        ],
        altitude: 120, // feet
        speed: 25, // mph
        ftcCost: 10,
        timestamp: new Date().toISOString(),
        submitter: stakerAccountId
    };

    console.log("✈️ Submitting flight plan:");
    console.log(`   Drone ID: ${flightPlan.droneId}`);
    console.log(`   Time: ${flightPlan.start} to ${flightPlan.end}`);
    console.log(`   Path: ${flightPlan.path.length} waypoints`);
    console.log(`   FTC Cost: ${flightPlan.ftcCost}`);

    try {
        // Submit flight plan as HCS message
        const message = JSON.stringify(flightPlan);
        const submitTx = await new TopicMessageSubmitTransaction()
            .setTopicId(topicId)
            .setMessage(message)
            .execute(client);

        const submitRx = await submitTx.getReceipt(client);
        console.log(`✅ Flight plan submitted! Transaction ID: ${submitRx.transactionId}`);

        // Pay FTC cost (transfer to operator)
        console.log(`💸 Paying ${flightPlan.ftcCost} FTC for flight plan submission...`);

        const paymentTx = await new TransferTransaction()
            .addTokenTransfer(ftcTokenId, stakerAccountId, -flightPlan.ftcCost)
            .addTokenTransfer(ftcTokenId, operatorId, flightPlan.ftcCost)
            .execute(client);

        await paymentTx.getReceipt(client);
        console.log(`✅ ${flightPlan.ftcCost} FTC paid to operator`);

        // Check new balance
        const newBalance = await new AccountBalanceQuery()
            .setAccountId(stakerAccountId)
            .execute(client);

        const newFtcBalance = newBalance.tokens._map.get(ftcTokenId) || 0;
        console.log(`💰 New FTC balance: ${newFtcBalance}`);

        console.log(`\n🎉 Flight plan successfully submitted to Hedera Consensus Service!`);
        console.log(`📊 Message will be ordered and consensus reached by the network`);

    } catch (error) {
        console.error("❌ Failed to submit flight plan:", error.message);
    }
}

main().catch(console.error);
