const { Wallet } = require("ethers")

const test_message = JSON.parse(process.argv[2])
const test_key = process.argv[3]

const wallet = new Wallet(test_key)

delete test_message.types.EIP712Domain

async function getSignature() {
    const signature = await wallet.signTypedData(test_message.domain, test_message.types, test_message.message)
    console.log(signature)
}

getSignature()
