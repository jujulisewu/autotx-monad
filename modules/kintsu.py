#!/usr/bin/env python3
import os
import sys
import time
from dotenv import load_dotenv
from web3 import Web3
from colorama import init, Fore

init(autoreset=True)

def display_header():
    print(Fore.BLUE + "====================")
    print(Fore.BLUE + "     KINTSU Bot     ")
    print(Fore.BLUE + "====================\n")

load_dotenv()
display_header()

RPC_URL = "https://testnet-rpc.monad.xyz/"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    print(Fore.RED + "? Private key tidak ditemukan di .env")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

contract_address = Web3.to_checksum_address("0x2c9C959516e9AAEdB2C748224a41249202ca8BE7")
gas_limit_stake = 500000
gas_limit_unstake = 800000
STAKE_AMOUNT = w3.to_wei(0.1, 'ether')
UNSTAKE_DELAY = 5 * 60  # 5 menit

def get_gas_price():
    return w3.eth.gas_price

def stake_mon():
    try:
        print(Fore.BLUE + "??  Starting KINTSU staking")
        print(Fore.MAGENTA + f"?? Staking: {w3.from_wei(STAKE_AMOUNT, 'ether')} MON")

        tx = {
            'to': contract_address,
            'data': "0xd5575982",  # stake()
            'gas': gas_limit_stake,
            'value': STAKE_AMOUNT,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': get_gas_price(),
            'chainId': w3.eth.chain_id
        }

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(Fore.YELLOW + f"??  Tx Hash: {EXPLORER_URL}{tx_hash.hex()}")
        print(Fore.LIGHTBLACK_EX + "? Waiting for confirmation...")

        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(Fore.GREEN + "? Stake DONE")
        return STAKE_AMOUNT

    except Exception as error:
        print(Fore.RED + f"? Staking failed: {error}")
        raise error

def unstake_gmon(amount_to_unstake):
    try:
        print(Fore.CYAN + f"?? Unstaking: {w3.from_wei(amount_to_unstake, 'ether')} gMON")

        # function selector: withdraw(uint256)
        function_selector = "0x6fed1ea7"
        padded_amount = amount_to_unstake.to_bytes(32, byteorder='big').hex()
        data = function_selector + padded_amount

        tx = {
            'to': contract_address,
            'data': data,
            'gas': gas_limit_unstake,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': get_gas_price(),
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
        print(Fore.LIGHTBLACK_EX + f"? Waiting {UNSTAKE_DELAY // 60} minutes before unstaking...\n")
        time.sleep(UNSTAKE_DELAY)
        unstake_gmon(stake_amount)

    except Exception as error:
        print(Fore.RED + f"? Failed: {error}")

if __name__ == '__main__':
    run_auto_cycle()
