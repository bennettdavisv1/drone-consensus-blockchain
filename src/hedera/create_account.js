import dotenv from "dotenv";
dotenv.config();
import {
    Client,
    PrivateKey,
    AccountCreateTransaction,
    Hbar,
    AccountBalanceQuery
} from "@hashgraph/sdk";

async function main() {
    const client = Client.forNetwork({
        "127.0.0.1:50211": "0.0.3"
    }).setMirrorNetwork("127.0.0.1:5600");

    const operatorKey = PrivateKey.fromStringED25519(process.env.OPERATOR_KEY);
    client.setOperator(process.env.OPERATOR_ID, operatorKey);

    console.log("🔐 Using operator account:", process.env.OPERATOR_ID);

    const newKey = PrivateKey.generateED25519();
    console.log("🔑 Generated new staker private key:", newKey.toStringRaw());
    console.log("🔑 Generated new staker public key:", newKey.publicKey.toStringRaw());

    const txResponse = await new AccountCreateTransaction()
        .setKey(newKey.publicKey)
        .setInitialBalance(new Hbar(100))
        .execute(client);

    const receipt = await txResponse.getReceipt(client);
    const newAccountId = receipt.accountId;

    console.log(`✅ New account created! ID: ${newAccountId.toString()}`);

    const balance = await new AccountBalanceQuery()
        .setAccountId(newAccountId)
        .execute(client);

    console.log(`💰 Account balance: ${balance.hbars.toString()}`);
    console.log(`📊 Simulated stake: 100 HBAR for account ${newAccountId.toString()}`);
}

main();
