// mint_ftc.js
import {
    Client,
    PrivateKey,
    TokenCreateTransaction,
    TokenType,
    TokenSupplyType,
    TokenMintTransaction,
    TokenAssociateTransaction,
    TransferTransaction,
    AccountBalanceQuery
} from "@hashgraph/sdk";

async function main() {
    // Operator (treasury) configuration
    const operatorId = "0.0.2";
    const operatorKey = PrivateKey.fromStringED25519(
        "REDACTED_PRIVATE_KEY"
    );

    const client = Client.forNetwork({
        "127.0.0.1:50211": "0.0.3"
    }).setMirrorNetwork("127.0.0.1:5600");

    client.setOperator(operatorId, operatorKey);

    console.log("🏦 Using treasury account:", operatorId);

    // The staker account you created earlier
    const stakerAccountId = "0.0.1002";
    const stakerKey = PrivateKey.fromStringED25519(
        "REDACTED_PRIVATE_KEY"
    );

    // Step 1: Create the FTC token
    console.log("\n🪙 Creating Flight Throughput Credit (FTC) token...");

    const tokenCreateTx = await new TokenCreateTransaction()
        .setTokenName("Flight Throughput Credit")
        .setTokenSymbol("FTC")
        .setTreasuryAccountId(operatorId)
        .setInitialSupply(0)
        .setTokenType(TokenType.FungibleCommon)
        .setSupplyType(TokenSupplyType.Infinite)
        .setDecimals(0)
        .setAdminKey(operatorKey.publicKey)
        .setSupplyKey(operatorKey.publicKey)
        .freezeWith(client)
        .sign(operatorKey); // ✅ must sign by treasury/admin

    const tokenCreateSubmit = await tokenCreateTx.execute(client);
    const tokenCreateRx = await tokenCreateSubmit.getReceipt(client);
    const tokenId = tokenCreateRx.tokenId;
    console.log(`✅ FTC token created! Token ID: ${tokenId.toString()}`);

    // Step 2: Associate the staker account with the token
    console.log("\n🔗 Associating staker account with FTC token...");

    const associateTx = await new TokenAssociateTransaction()
        .setAccountId(stakerAccountId)
        .setTokenIds([tokenId])
        .freezeWith(client)
        .sign(stakerKey);

    const associateSubmit = await associateTx.execute(client);
    await associateSubmit.getReceipt(client);
    console.log(`✅ Associated staker account (${stakerAccountId}) with token ${tokenId}`);

    // Step 3: Mint FTCs based on stake (1 FTC per 1 HBAR staked)
    const mintedAmount = 100;
    console.log(`\n💰 Minting ${mintedAmount} FTCs to treasury...`);

    const mintTx = await new TokenMintTransaction()
        .setTokenId(tokenId)
        .setAmount(mintedAmount)
        .freezeWith(client)
        .sign(operatorKey); // ✅ must sign by supply key

    const mintSubmit = await mintTx.execute(client);
    await mintSubmit.getReceipt(client);
    console.log(`✅ ${mintedAmount} FTCs minted.`);

    // Step 4: Transfer FTCs to staker
    console.log("\n🚀 Transferring FTCs to staker...");
    const transferTx = await new TransferTransaction()
        .addTokenTransfer(tokenId, operatorId, -mintedAmount)
        .addTokenTransfer(tokenId, stakerAccountId, mintedAmount)
        .freezeWith(client)
        .sign(operatorKey); // ✅ treasury must sign

    const transferSubmit = await transferTx.execute(client);
    await transferSubmit.getReceipt(client);
    console.log(`✅ ${mintedAmount} FTCs transferred to ${stakerAccountId}`);

    // Step 5: Query final balances
    const treasuryBalance = await new AccountBalanceQuery()
        .setAccountId(operatorId)
        .execute(client);

    const stakerBalance = await new AccountBalanceQuery()
        .setAccountId(stakerAccountId)
        .execute(client);

    console.log(`\n📊 Final balances:`);
    console.log(`   Treasury: ${treasuryBalance.tokens._map.get(tokenId.toString()) || 0} FTC`);
    console.log(`   Staker: ${stakerBalance.tokens._map.get(tokenId.toString()) || 0} FTC`);

    console.log("\n🎉 Flight Throughput Credit minting complete!");
}

main();
