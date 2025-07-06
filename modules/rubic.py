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
    print(Fore.BLUE + "     RUBIC Bot      ")
    print(Fore.BLUE + "====================")

load_dotenv()
displayHeader()

RPC_URL = "https://testnet-rpc.monad.xyz/"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    print(Fore.RED + "? Private key tidak ditemukan di file .env!")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

WMON_CONTRACT = "0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701"

# ABI fungsi deposit dan withdraw
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
    return w3.to_wei(round(random.uniform(0.01, 0.05), 4), 'ether')

def getRandomDelay():
    return random.randint(60_000, 180_000)  # 1 - 3 menit

def wrapMON(amount):
    try:
        print()
        print(Fore.MAGENTA + f"?? Wrap {w3.from_wei(amount, 'ether')} MON ? WMON")
        tx = contract.functions.deposit().build_transaction({
            'from': account.address,
            'value': amount,
            'gas': 500000,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.GREEN + "? Wrap berhasil")
        print(Fore.YELLOW + f"??  Tx Hash: {EXPLORER_URL}{tx_hash.hex()}")
        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as error:
        print(Fore.RED + f"? Gagal wrap MON: {error}")

def unwrapMON(amount):
    try:
        print(Fore.MAGENTA + f"?? Unwrap {w3.from_wei(amount, 'ether')} WMON ? MON")
        tx = contract.functions.withdraw(amount).build_transaction({
            'from': account.address,
            'gas': 500000,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.GREEN + "? Unwrap berhasil")
        print(Fore.YELLOW + f"??  Tx Hash: {EXPLORER_URL}{tx_hash.hex()}")
        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as error:
        print(Fore.RED + f"? Gagal unwrap WMON: {error}")

def runSwapCycle(cycles=1):
    for i in range(cycles):
        amount = getRandomAmount()
        delay_ms = getRandomDelay()
        wrapMON(amount)
        unwrapMON(amount)
        print(Fore.LIGHTBLACK_EX + f"? Menunggu {delay_ms // 1000 // 60} menit...")
        time.sleep(delay_ms / 1000)

if __name__ == '__main__':
    print(Fore.BLUE + "?? Memulai RUBIC Bot... ??????")
    runSwapCycle()
