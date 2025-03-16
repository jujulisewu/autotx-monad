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
    print(Fore.BLUE + "      RUBIC Bot     ")
    print(Fore.BLUE + "====================")

load_dotenv()
displayHeader()

RPC_URL = "https://testnet-rpc.monad.xyz/"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    print(Fore.RED + "❌ Private key tidak ditemukan!")
    sys.exit(1)
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
WMON_CONTRACT = "0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701"

# ABI untuk fungsi deposit dan withdraw
contract = w3.eth.contract(address=WMON_CONTRACT, abi=[
    {
        "constant": False,
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [{"name": "amount", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
])

def getRandomAmount():
    min_val = 0.01
    max_val = 0.05
    randomAmount = random.uniform(min_val, max_val)
    return w3.to_wei(round(randomAmount, 4), 'ether')

def getRandomDelay():
    minDelay = 1 * 60 * 1000
    maxDelay = 3 * 60 * 1000
    return random.randint(minDelay, maxDelay)

def wrapMON(amount):
    try:
        print(" ")
        print(Fore.MAGENTA + f"🔄 Wrap {w3.from_wei(amount, 'ether')} MON > WMON")
        tx = contract.functions.deposit().build_transaction({
            'from': account.address,
            'value': amount,
            'gas': 500000,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.GREEN + "✅ Wrap MON > WMON successful")
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as error:
        print(Fore.RED + f"❌ Error wrap MON: {error}")

def unwrapMON(amount):
    try:
        print(Fore.MAGENTA + f"🔄 Unwrap {w3.from_wei(amount, 'ether')} WMON > MON")
        tx = contract.functions.withdraw(amount).build_transaction({
            'from': account.address,
            'gas': 500000,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.GREEN + "✅ Unwrap WMON > MON successful")
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as error:
        print(Fore.RED + f"❌ Error unwrapping WMON: {error}")

def runSwapCycle(cycles=1, interval=None):
    for i in range(cycles):
        randomAmount = getRandomAmount()
        randomDelay = getRandomDelay()
        wrapMON(randomAmount)
        unwrapMON(randomAmount)
        print(Fore.WHITE + f"⏳ Wait {randomDelay / 1000 / 60} Minute")
        time.sleep(randomDelay / 1000)

if __name__ == '__main__':
    print(Fore.BLUE + "🪫  Starting Rubic ⏩⏩⏩⏩")
    runSwapCycle()
