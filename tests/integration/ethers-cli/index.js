#!/usr/bin/env node

const ethers = require('ethers');
const yargs = require('yargs');

const options = yargs
    .usage("Usage: -m <mnemonic>")
    .option("m", {
        alias: "mnemonic",
        describe: "BIP39 Mnemonic seed phrase",
        type: "array",
        demandOption: true,
    })
    .option("l", {
        alias: "language",
        describe: "Wordlist language used for mnemonic",
        type: "String",
    })
    .option("p", {
        alias: "path",
        describe: "HD Path used for derivation",
        type: "String",
    })
    .argv;

var wordlist;

switch(options.language) {
    case "english":
        wordlist = ethers.wordlists.en;
        break;
    case "spanish":
        wordlist = ethers.wordlists.es;
        break;
    case "french":
        wordlist = ethers.wordlists.fr;
        break;
    case "italian":
        wordlist = ethers.wordlists.it;
        break;
    case "czech":
        wordlist = ethers.wordlists.cz;
        break;
    case "japanese":
        wordlist = ethers.wordlists.ja;
        break;
    case "korean":
        wordlist = ethers.wordlists.ko;
        break;
    case "chinese_simplified":
        wordlist = ethers.wordlists.zh_cn;
        break;
    case "chinese_traditional":
        wordlist = ethers.wordlists.zh_tw;
        break;
    default:
        wordlist = ethers.wordlists.en;
}

// If specified, use the given path, else default to Ethereum
const path = options.path ? options.path : "m/44'/60'/0'/0/0";

const account = ethers.HDNodeWallet.fromPhrase(
    options.mnemonic.join(" "),
    undefined, // an optional password arg that we don't use
    path,
    wordlist,
);

console.log(account.address);
