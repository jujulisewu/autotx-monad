#!/usr/bin/env python3
import os, sys, time, random
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

def display_header():
    print(Style.BRIGHT + Fore.CYAN + "======================================")
    print(Style.BRIGHT + Fore.CYAN + "             Izumi Bot               ")
    print(Style.BRIGHT + Fore.CYAN + "======================================\n")

display_header()

# Config
RPC_URL = "https://testnet-rpc.monad.xyz/"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    raise Exception("? PRIVATE_KEY not found in .env")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)
WMON_CONTRACT = Web3.to_checksum_address("0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701")

# Minimal ABI
contract_abi = [
    {
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=WMON_CONTRACT, abi=contract_abi)

# Helpers
def get_random_amount():
    amount = random.uniform(0.01, 0.05)
    return w3.to_wei(round(amount, 4), "ether")

def get_random_delay():
    return random.randint(60_000, 180_000)  # ms

# Actions
def wrap_mon(amount):
    try:
        print(Fore.BLUE + "?? Starting Wrap MON ? WMON")
        print(Fore.MAGENTA + f"?? Wrapping {w3.from_wei(amount, 'ether')} MON")

        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.deposit().build_transaction({
            'from': account.address,
            'value': amount,
            'gas': 500_000,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price
        })

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.GREEN + "? Wrap transaction sent.")
        print(Fore.LIGHTBLACK_EX + f"?? Explorer: {EXPLORER_URL}/{tx_hash.hex()}")

        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        print(Fore.RED + f"? Error wrapping MON: {e}")

def unwrap_mon(amount):
    try:
        print(Fore.BLUE + f"?? Unwrapping {w3.from_wei(amount, 'ether')} WMON ? MON")

        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.withdraw(amount).build_transaction({
            'from': account.address,
            'gas': 500_000,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price
        })

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.GREEN + "? Unwrap transaction sent.")
        print(Fore.LIGHTBLACK_EX + f"?? Explorer: {EXPLORER_URL}/{tx_hash.hex()}")

        w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        print(Fore.RED + f"? Error unwrapping WMON: {e}")

def run_swap_cycle(cycles=1):
    try:
        for i in range(cycles):
            amount = get_random_amount()
            delay = get_random_delay()

            print(Fore.YELLOW + f"\n?? Cycle {i+1}/{cycles}")
            wrap_mon(amount)
            unwrap_mon(amount)

            if i < cycles - 1:
                wait_minutes = delay / 1000 / 60
                print(Fore.LIGHTBLACK_EX + f"? Waiting {wait_minutes:.2f} minutes...\n")
                time.sleep(delay / 1000)

        print(Fore.GREEN + Style.BRIGHT + "\n?? Izumi swap cycles completed.\n")
    except Exception as e:
        print(Fore.RED + f"? Error in run_swap_cycle: {e}")

if __name__ == '__main__':
    try:
        run_swap_cycle(1)
    except Exception as e:
        print(Fore.RED + f"? Fatal error: {e}")
