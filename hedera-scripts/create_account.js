// create_account.js
import {
    Client,
    PrivateKey,
    AccountCreateTransaction,
    Hbar,
    AccountBalanceQuery
} from "@hashgraph/sdk";

async function main() {
    // The operator account (0.0.2) is pre-funded in the local node
    const operatorId = "0.0.2";
    const operatorKey = PrivateKey.fromStringED25519(
        "REDACTED_PRIVATE_KEY"
    );

    const client = Client.forNetwork({
        "127.0.0.1:50211": "0.0.3"
    }).setMirrorNetwork("127.0.0.1:5600");

    client.setOperator(operatorId, operatorKey);

    console.log("🔐 Using operator account:", operatorId);

    // Generate a new keypair for the staker account
    const newKey = PrivateKey.generateED25519();

    console.log("🔑 Generated new staker private key:", newKey.toStringRaw());
    console.log("🔑 Generated new staker public key:", newKey.publicKey.toStringRaw());

    // Create a new account with initial balance
    const txResponse = await new AccountCreateTransaction()
        .setKey(newKey.publicKey)
        .setInitialBalance(new Hbar(100))
        .execute(client);

    const receipt = await txResponse.getReceipt(client);
    const newAccountId = receipt.accountId;

    console.log(`✅ New account created! ID: ${newAccountId.toString()}`);

    // Query balance
    const balance = await new AccountBalanceQuery()
        .setAccountId(newAccountId)
        .execute(client);

    console.log(`💰 Account balance: ${balance.hbars.toString()}`);

    console.log(`📊 Simulated stake: 100 HBAR for account ${newAccountId.toString()}`);
    console.log("🏗️ Ready for Flight Throughput Credit minting phase.");
}

main();
