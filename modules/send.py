#!/usr/bin/env python3
import os
import sys
import time
import random
from dotenv import load_dotenv
from web3 import Web3
from colorama import init, Fore

init(autoreset=True)

def displayHeader():
    print(Fore.BLUE + "====================")
    print(Fore.BLUE + "    AUTOSEND Bot    ")
    print(Fore.BLUE + "====================")

load_dotenv()
displayHeader()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    print(Fore.RED + "Private key tidak ditemukan di .env")
    sys.exit(1)

network = {
    "name": "Monad Testnet",
    "chainId": 10143,
    "rpc": "https://testnet-rpc.monad.xyz",
    "symbol": "MON",
    "explorer": "https://testnet.monadexplorer.com"
}

w3 = Web3(Web3.HTTPProvider(network["rpc"]))

def generateNewWallet():
    new_account = w3.eth.account.create()
    # Menggunakan atribut 'key' untuk mendapatkan private key
    return {
        "address": new_account.address,
        "privateKey": new_account.key.hex()
    }

def transferTokens(wallet, index):
    newWallet = generateNewWallet()
    # Menghasilkan nilai random antara 0.0001 dan 0.001 dengan 6 desimal
    randomAmount = max(random.uniform(0.0001, 0.001), 0.0001)
    randomAmount_str = f"{randomAmount:.6f}"
    tx = {
        'to': newWallet["address"],
        # Konversi dengan asumsi token memiliki 6 desimal
        'value': int(float(randomAmount_str) * (10 ** 6)),
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(wallet.address)
    }
    signed_tx = wallet.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    shortAddress = newWallet["address"][-5:]
    print(Fore.GREEN + f"✅ ({index + 1}/50) [confirm] : {randomAmount_str} {network['symbol']} sent to {shortAddress} : {tx_hash.hex()}")

def handleTokenTransfers():
    wallet = w3.eth.account.from_key(PRIVATE_KEY)
    print(Fore.BLUE + "🪫  Starting AutoSend ⏩⏩⏩⏩")
    print(" ")
    for i in range(50):
        transferTokens(wallet, i)
    print(Fore.GREEN + "⏩ \nAll transactions completed successfully!")

if __name__ == '__main__':
    try:
        handleTokenTransfers()
    except Exception as e:
        print(str(e))
