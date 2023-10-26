const { SignTypedDataVersion } = require("@metamask/eth-sig-util/sign-typed-data")
const ethSigUtil = require("@metamask/eth-sig-util")

const test_message_json = JSON.parse(process.argv[2])
const test_key = process.argv[3]

let v4 = SignTypedDataVersion.V4
sig = ethSigUtil.signTypedData({privateKey: test_key, data: test_message_json, version: v4})

console.log(sig)
