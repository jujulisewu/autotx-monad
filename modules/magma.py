#!/usr/bin/env python3
import os
import sys
import time
import random
from dotenv import load_dotenv
from web3 import Web3
from colorama import init, Fore

init(autoreset=True)
load_dotenv()

def display_header():
    print(Fore.BLUE + "====================")
    print(Fore.BLUE + "     MAGMA Bot      ")
    print(Fore.BLUE + "====================")

display_header()

RPC_URL = "https://testnet-rpc.monad.xyz"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    print(Fore.RED + "? Private key tidak ditemukan di .env")
    sys.exit(1)

account = w3.eth.account.from_key(PRIVATE_KEY)

contract_address = "0x2c9C959516e9AAEdB2C748224a41249202ca8BE7"
gas_limit_stake = 500_000
gas_limit_unstake = 800_000

def get_random_amount():
    min_val = 0.01
    max_val = 0.05
    amount = round(random.uniform(min_val, max_val), 4)
    return w3.to_wei(amount, 'ether')

def delay(ms):
    time.sleep(ms / 1000)

def stake_mon():
    try:
        stake_amount = get_random_amount()
        print(Fore.BLUE + "?? Starting MAGMA Stake")
        print(Fore.MAGENTA + f"?? Staking {w3.from_wei(stake_amount, 'ether')} MON")

        tx = {
            'to': contract_address,
            'data': "0xd5575982",  # stake()
            'gas': gas_limit_stake,
            'value': stake_amount,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        }

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(Fore.YELLOW + f"??  Tx Hash: {EXPLORER_URL}{tx_hash.hex()}")
        print(Fore.LIGHTBLACK_EX + "? Waiting for confirmation...")
        w3.eth.wait_for_transaction_receipt(tx_hash)

        print(Fore.GREEN + "? Stake DONE")
        return stake_amount
    except Exception as error:
        print(Fore.RED + f"? Staking failed: {error}")
        raise error

def unstake_gmon(amount):
    try:
        print(Fore.CYAN + f"?? Unstaking {w3.from_wei(amount, 'ether')} gMON")

        function_selector = "0x6fed1ea7"  # withdraw(uint256)
        padded_amount = amount.to_bytes(32, byteorder='big').hex()
        data = function_selector + padded_amount

        tx = {
            'to': contract_address,
            'data': data,
            'gas': gas_limit_unstake,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        }

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(Fore.YELLOW + f"??  Tx Hash: {EXPLORER_URL}{tx_hash.hex()}")
        print(Fore.LIGHTBLACK_EX + "? Waiting for confirmation...")
        w3.eth.wait_for_transaction_receipt(tx_hash)

        print(Fore.GREEN + "? Unstake DONE")
    except Exception as error:
        print(Fore.RED + f"? Unstaking failed: {error}")
        raise error

def run_auto_cycle():
    try:
        stake_amount = stake_mon()
        wait_ms = 73383
        print(Fore.LIGHTBLACK_EX + f"? Waiting {wait_ms/1000:.2f} seconds before unstaking...")
        delay(wait_ms)
        unstake_gmon(stake_amount)
    except Exception as error:
        print(Fore.RED + f"? Failed: {error}")

if __name__ == '__main__':
    run_auto_cycle()
