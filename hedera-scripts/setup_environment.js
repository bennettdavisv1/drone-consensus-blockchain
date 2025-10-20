import dotenv from "dotenv";
dotenv.config();
import {
    Client,
    PrivateKey,
    TopicCreateTransaction,
    TokenCreateTransaction,
    TokenType,
    TokenSupplyType,
    TokenMintTransaction,
    TokenAssociateTransaction,
    TransferTransaction,
    AccountCreateTransaction,
    Hbar,
    AccountBalanceQuery
} from "@hashgraph/sdk";

async function main() {
    console.log("🚀 Setting up complete Hedera environment for drone consensus...\n");

    const client = Client.forNetwork({
        "127.0.0.1:50211": "0.0.3"
    }).setMirrorNetwork("127.0.0.1:5600");

    const operatorKey = PrivateKey.fromStringED25519(process.env.OPERATOR_KEY);
    client.setOperator(process.env.OPERATOR_ID, operatorKey);

    console.log("🔐 Using operator account:", process.env.OPERATOR_ID);

    try {
        // Step 1: Create staker account
        console.log("\n1️⃣ Creating staker account...");
        const newKey = PrivateKey.generateED25519();
        const txResponse = await new AccountCreateTransaction()
            .setKey(newKey.publicKey)
            .setInitialBalance(new Hbar(100))
            .execute(client);

        const receipt = await txResponse.getReceipt(client);
        const stakerAccountId = receipt.accountId;
        console.log(`✅ Staker account created: ${stakerAccountId.toString()}`);
        console.log(`🔑 Staker private key: ${newKey.toStringRaw()}`);

        // Step 2: Create FTC token
        console.log("\n2️⃣ Creating Flight Throughput Credit (FTC) token...");
        const tokenCreateTx = await new TokenCreateTransaction()
            .setTokenName("Flight Throughput Credit")
            .setTokenSymbol("FTC")
            .setTreasuryAccountId(process.env.OPERATOR_ID)
            .setInitialSupply(0)
            .setTokenType(TokenType.FungibleCommon)
            .setSupplyType(TokenSupplyType.Infinite)
            .setDecimals(0)
            .setAdminKey(operatorKey.publicKey)
            .setSupplyKey(operatorKey.publicKey)
            .freezeWith(client)
            .sign(operatorKey);

        const tokenCreateSubmit = await tokenCreateTx.execute(client);
        const tokenCreateRx = await tokenCreateSubmit.getReceipt(client);
        const tokenId = tokenCreateRx.tokenId;
        console.log(`✅ FTC token created: ${tokenId.toString()}`);

        // Step 3: Associate staker with token
        console.log("\n3️⃣ Associating staker account with FTC token...");
        const associateTx = await new TokenAssociateTransaction()
            .setAccountId(stakerAccountId)
            .setTokenIds([tokenId])
            .freezeWith(client)
            .sign(newKey);

        await (await associateTx.execute(client)).getReceipt(client);
        console.log(`✅ Staker account associated with FTC token`);

        // Step 4: Mint and transfer FTCs
        console.log("\n4️⃣ Minting and transferring 100 FTCs to staker...");
        const mintTx = await new TokenMintTransaction()
            .setTokenId(tokenId)
            .setAmount(100)
            .freezeWith(client)
            .sign(operatorKey);

        await (await mintTx.execute(client)).getReceipt(client);

        const transferTx = await new TransferTransaction()
            .addTokenTransfer(tokenId, process.env.OPERATOR_ID, -100)
            .addTokenTransfer(tokenId, stakerAccountId, 100)
            .freezeWith(client)
            .sign(operatorKey);

        await (await transferTx.execute(client)).getReceipt(client);
        console.log(`✅ 100 FTCs transferred to staker`);

        // Step 5: Create HCS topic for flight plans
        console.log("\n5️⃣ Creating HCS topic for flight plan submissions...");
        const topicCreateTx = await new TopicCreateTransaction()
            .setTopicMemo("Drone Flight Plan Consensus Topic")
            .execute(client);

        const topicCreateRx = await topicCreateTx.getReceipt(client);
        const topicId = topicCreateRx.topicId;
        console.log(`✅ Flight plan topic created: ${topicId.toString()}`);

        // Step 6: Display final balances
        console.log("\n6️⃣ Final account balances:");
        const stakerBalance = await new AccountBalanceQuery()
            .setAccountId(stakerAccountId)
            .execute(client);

        const ftcBalance = stakerBalance.tokens._map.get(tokenId.toString()) || 0;
        console.log(`   Staker HBAR: ${stakerBalance.hbars.toString()}`);
        console.log(`   Staker FTC: ${ftcBalance}`);

        // Step 7: Generate .env file content
        console.log("\n📝 Environment setup complete! Add these to your .env file:");
        console.log("─".repeat(60));
        console.log(`OPERATOR_ID=${process.env.OPERATOR_ID}`);
        console.log(`OPERATOR_KEY=${process.env.OPERATOR_KEY}`);
        console.log(`STAKER_ID=${stakerAccountId.toString()}`);
        console.log(`STAKER_KEY=${newKey.toStringRaw()}`);
        console.log(`FTC_TOKEN_ID=${tokenId.toString()}`);
        console.log(`FLIGHT_PLAN_TOPIC_ID=${topicId.toString()}`);
        console.log("─".repeat(60));

        console.log("\n🎯 Next steps:");
        console.log("1. Update your .env file with the values above");
        console.log("2. Test flight plan submission: node submit_flightplan.js");
        console.log("3. Start message consumer: node consume_flightplans.js");
        console.log("4. Run integrated API: python hedera_flight_api.py");

    } catch (error) {
        console.error("❌ Setup failed:", error.message);
    }
}

main().catch(console.error);
