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
    print(Fore.RED + "? Private key tidak ditemukan di .env")
    sys.exit(1)

network = {
    "name": "Monad Testnet",
    "chainId": 10143,
    "rpc": "https://testnet-rpc.monad.xyz",
    "symbol": "MON",
    "explorer": "https://testnet.monadexplorer.com/tx/"
}

w3 = Web3(Web3.HTTPProvider(network["rpc"]))

if not w3.is_connected():
    print(Fore.RED + "? Gagal terhubung ke RPC Monad")
    sys.exit(1)

def generateNewWallet():
    account = w3.eth.account.create()
    return {
        "address": account.address,
        "privateKey": account.key.hex()
    }

def transferTokens(wallet, index):
    new_wallet = generateNewWallet()
    random_amount = round(random.uniform(0.0001, 0.001), 6)  # in MON
    wei_amount = w3.to_wei(random_amount, 'ether')

    try:
        nonce = w3.eth.get_transaction_count(wallet.address)
        tx = {
            'to': new_wallet["address"],
            'value': wei_amount,
            'gas': 21000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
            'chainId': network["chainId"]
        }

        signed_tx = wallet.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        short_address = new_wallet["address"][-5:]

        print(Fore.GREEN + f"? ({index + 1}/50) Sent {random_amount:.6f} {network['symbol']} ? {short_address}")
        print(Fore.YELLOW + f"?? Tx: {network['explorer']}{tx_hash.hex()}")

    except Exception as e:
        print(Fore.RED + f"? Error saat transfer ke wallet {new_wallet['address']}: {e}")

def handleTokenTransfers():
    wallet = w3.eth.account.from_key(PRIVATE_KEY)
    print(Fore.BLUE + "?? Starting AutoSend ??")
    print(" ")

    for i in range(50):
        transferTokens(wallet, i)
        time.sleep(1.5)  # optional delay between txs

    print(Fore.GREEN + "\n?? Semua transaksi selesai dengan sukses!")

if __name__ == '__main__':
    try:
        handleTokenTransfers()
    except Exception as e:
        print(Fore.RED + f"? Error utama: {e}")
