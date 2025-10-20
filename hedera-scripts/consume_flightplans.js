import dotenv from "dotenv";
dotenv.config();
import {
    Client,
    PrivateKey,
    TopicMessageQuery,
    TopicId
} from "@hashgraph/sdk";

async function main() {
    const client = Client.forNetwork({
        "127.0.0.1:50211": "0.0.3"
    }).setMirrorNetwork("127.0.0.1:5600");

    const operatorKey = PrivateKey.fromStringED25519(process.env.OPERATOR_KEY);
    client.setOperator(process.env.OPERATOR_ID, operatorKey);

    const topicId = process.env.FLIGHT_PLAN_TOPIC_ID;

    if (!topicId) {
        console.error("❌ FLIGHT_PLAN_TOPIC_ID not found in .env file");
        console.log("💡 Run: node create_topic.js first");
        return;
    }

    console.log("🔍 Starting flight plan message consumption...");
    console.log(`📡 Listening to topic: ${topicId}`);
    console.log("⏳ Waiting for flight plan submissions...\n");

    // Store flight plans for conflict detection
    const flightPlans = [];
    const conflicts = [];

    function detectConflicts(newPlan) {
        const newStart = new Date(newPlan.start);
        const newEnd = new Date(newPlan.end);

        for (const existingPlan of flightPlans) {
            const existingStart = new Date(existingPlan.start);
            const existingEnd = new Date(existingPlan.end);

            // Check for time overlap
            if (newStart < existingEnd && existingStart < newEnd) {
                const conflict = {
                    newPlan: newPlan.droneId,
                    existingPlan: existingPlan.droneId,
                    timeOverlap: {
                        new: `${newPlan.start} to ${newPlan.end}`,
                        existing: `${existingPlan.start} to ${existingPlan.end}`
                    },
                    status: "CONFLICT_DETECTED"
                };
                conflicts.push(conflict);
                return conflict;
            }
        }
        return null;
    }

    // Start consuming messages from the topic
    new TopicMessageQuery()
        .setTopicId(topicId)
        .setStartTime(0) // Start from the beginning
        .subscribe(client, (message) => {
            try {
                const flightPlan = JSON.parse(message.contents.toString());

                console.log("📨 New flight plan received:");
                console.log(`   Drone ID: ${flightPlan.droneId}`);
                console.log(`   Time: ${flightPlan.start} to ${flightPlan.end}`);
                console.log(`   Path: ${flightPlan.path.length} waypoints`);
                console.log(`   FTC Cost: ${flightPlan.ftcCost}`);
                console.log(`   Submitter: ${flightPlan.submitter}`);
                console.log(`   Timestamp: ${flightPlan.timestamp}`);

                // Check for conflicts
                const conflict = detectConflicts(flightPlan);

                if (conflict) {
                    console.log("⚠️  CONFLICT DETECTED!");
                    console.log(`   New plan: ${conflict.newPlan}`);
                    console.log(`   Conflicts with: ${conflict.existingPlan}`);
                    console.log(`   Time overlap: ${conflict.timeOverlap.new} vs ${conflict.timeOverlap.existing}`);
                    console.log("   Status: DENIED ❌\n");
                } else {
                    console.log("✅ No conflicts detected - APPROVED");
                    console.log("   Status: APPROVED ✅\n");
                }

                // Store the flight plan
                flightPlans.push(flightPlan);

                // Display current status
                console.log(`📊 Total flight plans: ${flightPlans.length}`);
                console.log(`⚠️  Total conflicts: ${conflicts.length}`);
                console.log("─".repeat(50));

            } catch (error) {
                console.error("❌ Error processing message:", error.message);
            }
        }, (error) => {
            console.error("❌ Subscription error:", error.message);
        });

    console.log("🎯 Flight plan consumer is now running...");
    console.log("💡 Submit flight plans using: node submit_flightplan.js");
    console.log("🛑 Press Ctrl+C to stop\n");
}

main().catch(console.error);
