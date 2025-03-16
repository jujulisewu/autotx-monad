#!/usr/bin/env python3
import os, sys, time, random, requests
from dotenv import load_dotenv
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

def display_header():
    print(Style.BRIGHT + Fore.CYAN + "======================================")
    print(Style.BRIGHT + Fore.CYAN + "            Apriori Bot               ")
    print(Style.BRIGHT + Fore.CYAN + "====================================\n")

# Konfigurasi
RPC_URL = "https://testnet-rpc.monad.xyz"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    print(Fore.RED + "❌ PRIVATE_KEY tidak ditemukan di .env")
    sys.exit(1)

account = Account.from_key(PRIVATE_KEY)
contract_address = Web3.to_checksum_address("0xb2f82D0f38dc453D596Ad40A37799446Cc89274A")

# Gas limit
GAS_LIMIT_STAKE = 500000
GAS_LIMIT_UNSTAKE = 800000
GAS_LIMIT_CLAIM = 800000


def hex_zero_pad(value, length_bytes=32):
    if isinstance(value, int):
        hex_str = hex(value)[2:]
    elif isinstance(value, str):
        hex_str = value[2:] if value.startswith("0x") else value
    else:
        raise TypeError("Tipe data tidak didukung untuk padding hex")
    return "0x" + hex_str.zfill(length_bytes * 2)


def hex_zero_pad_address(address, length_bytes=32):
    return "0x" + address[2:].lower().zfill(length_bytes * 2)


def get_random_amount():
    min_val = 0.01
    max_val = 0.05
    random_amount = round(random.uniform(min_val, max_val), 4)
    return w3.to_wei(random_amount, "ether")


def get_random_delay():
    min_delay = 1 * 60 * 1000  # dalam ms
    max_delay = 2 * 60 * 1000  # dalam ms
    return random.randint(min_delay, max_delay)


def delay(ms):
    time.sleep(ms / 1000)


def send_transaction(tx):
    tx['nonce'] = w3.eth.get_transaction_count(account.address)
    if 'gasPrice' not in tx:
        tx['gasPrice'] = w3.eth.gas_price
    signed_tx = account.sign_transaction(tx)
    # Perbaiki atribut rawTransaction menjadi raw_transaction
    return w3.eth.send_raw_transaction(signed_tx.raw_transaction)


def wait_for_receipt(tx_hash):
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def stake_mon():
    try:
        stake_amount = get_random_amount()
        print(Fore.GREEN + f"🔄 Stake: {Web3.from_wei(stake_amount, 'ether')} MON")
        data = "0x6e553f65" + hex_zero_pad(stake_amount, 32)[2:] + hex_zero_pad_address(account.address, 32)[2:]
        tx = {
            'to': contract_address,
            'value': stake_amount,
            'gas': GAS_LIMIT_STAKE,
            'data': data
        }
        tx_hash = send_transaction(tx)
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
        return wait_for_receipt(tx_hash), stake_amount
    except Exception as e:
        print(Fore.RED + f"❌ Staking failed: {str(e)}")
        raise


def request_unstake(amount_to_unstake):
    try:
        print(Fore.GREEN + f"🔄 Unstake: {Web3.from_wei(amount_to_unstake, 'ether')} aprMON")
        data = ("0x7d41c86e" +
                hex_zero_pad(amount_to_unstake, 32)[2:] +
                hex_zero_pad_address(account.address, 32)[2:] +
                hex_zero_pad_address(account.address, 32)[2:])
        tx = {
            'to': contract_address,
            'value': 0,
            'gas': GAS_LIMIT_UNSTAKE,
            'data': data
        }
        tx_hash = send_transaction(tx)
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
        return wait_for_receipt(tx_hash)
    except Exception as e:
        print(Fore.RED + f"❌ Unstake failed: {str(e)}")
        raise


def run_cycle():
    try:
        receipt, stake_amount = stake_mon()
        delay(get_random_delay())
        request_unstake(stake_amount)
        print(Fore.GREEN + "✅ Cycle complete")
    except Exception as e:
        print(Fore.RED + f"❌ Error in cycle: {str(e)}")


def main():
    display_header()
    print(Fore.BLUE + "\n🪫  Starting Apriori ⏩⏩⏩⏩\n")
    for i in range(1):
        run_cycle()
        delay(get_random_delay())


if __name__ == '__main__':
    main()
