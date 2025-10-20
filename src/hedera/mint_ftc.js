import dotenv from "dotenv";
dotenv.config();
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
    const client = Client.forNetwork({
        "127.0.0.1:50211": "0.0.3"
    }).setMirrorNetwork("127.0.0.1:5600");

    const operatorKey = PrivateKey.fromStringED25519(process.env.OPERATOR_KEY);
    const stakerKey = PrivateKey.fromStringED25519(process.env.STAKER_KEY);
    const operatorId = process.env.OPERATOR_ID;
    const stakerAccountId = process.env.STAKER_ID;

    client.setOperator(operatorId, operatorKey);
    console.log("🏦 Using treasury account:", operatorId);

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
        .sign(operatorKey);

    const tokenCreateSubmit = await tokenCreateTx.execute(client);
    const tokenCreateRx = await tokenCreateSubmit.getReceipt(client);
    const tokenId = tokenCreateRx.tokenId;
    console.log(`✅ FTC token created! Token ID: ${tokenId.toString()}`);

    const associateTx = await new TokenAssociateTransaction()
        .setAccountId(stakerAccountId)
        .setTokenIds([tokenId])
        .freezeWith(client)
        .sign(stakerKey);

    await (await associateTx.execute(client)).getReceipt(client);
    console.log(`✅ Associated staker account (${stakerAccountId}) with token ${tokenId}`);

    const mintedAmount = 100;
    console.log(`\n💰 Minting ${mintedAmount} FTCs to treasury...`);

    const mintTx = await new TokenMintTransaction()
        .setTokenId(tokenId)
        .setAmount(mintedAmount)
        .freezeWith(client)
        .sign(operatorKey);

    await (await mintTx.execute(client)).getReceipt(client);
    console.log(`✅ ${mintedAmount} FTCs minted.`);

    const transferTx = await new TransferTransaction()
        .addTokenTransfer(tokenId, operatorId, -mintedAmount)
        .addTokenTransfer(tokenId, stakerAccountId, mintedAmount)
        .freezeWith(client)
        .sign(operatorKey);

    await (await transferTx.execute(client)).getReceipt(client);
    console.log(`✅ ${mintedAmount} FTCs transferred to ${stakerAccountId}`);

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
