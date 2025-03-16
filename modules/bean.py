#!/usr/bin/env python3
import os
import json
import time
import re
import random
import requests
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

def display_header():
    print(Style.BRIGHT + Fore.CYAN + "======================================")
    print(Style.BRIGHT + Fore.CYAN + "            BeanSwap Bot              ")
    print(Style.BRIGHT + Fore.CYAN + "====================================\n")

display_header()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise Exception("No PrivateKey in .env")

# Daftar RPC
RPC_URLS = [
    "https://testnet-rpc.monad.xyz"
]

CHAIN_ID = 10143

# Alamat kontrak (pastikan valid)
ROUTER_CONTRACT = "0xCa810D095e90Daae6e867c19DF6D9A8C56db2c89"
WMON_CONTRACT = "0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701"
USDC_CONTRACT = "0xf817257fed379853cDe0fa4F97AB987181B1E5Ea"
BEAN_CONTRACT = "0x268E4E24E0051EC27b3D27A95977E71cE6875a05"
JAI_CONTRACT  = "0x70F893f65E3C1d7f82aad72f71615eb220b74D10"

TOKEN_ADDRESSES = {
    "WMON": WMON_CONTRACT,
    "USDC": USDC_CONTRACT,
    "BEAN": BEAN_CONTRACT,
    "JAI": JAI_CONTRACT
}

# URL untuk mengunduh ABI
ABI_URL = "https://raw.githubusercontent.com/shareithub/autotx-monad/refs/heads/main/abi/BEAN.js"

def fetch_abi(url):
    try:
        print(Fore.YELLOW + f"🔄 Mengunduh ABI dari {url}...")
        response = requests.get(url)
        response.raise_for_status()

        abi_content = response.text.strip()
        print("📜 Isi ABI yang diterima:", abi_content[:100])  # Debug isi ABI

        # Ekstrak hanya bagian JSON dari BEAN.js
        abi_match = re.search(r'const\s+ABI\s*=\s*(\[.*\]);?', abi_content, re.DOTALL)
        if not abi_match:
            raise ValueError("Format ABI tidak valid!")

        abi_json_str = abi_match.group(1)

        # Parsing JSON
        abi_json = json.loads(abi_json_str)
        
        print(Fore.GREEN + "✅ ABI berhasil diunduh dan diproses!\n")
        return abi_json
    except json.JSONDecodeError:
        raise Exception(Fore.RED + "❌ Gagal mengunduh ABI: Format JSON tidak valid!")
    except Exception as e:
        raise Exception(Fore.RED + f"❌ Gagal mengunduh ABI: {str(e)}")

# Muat ABI secara global
ABI = fetch_abi(ABI_URL)

def connect_to_rpc():
    for url in RPC_URLS:
        try:
            w3_instance = Web3(Web3.HTTPProvider(url))
            _ = w3_instance.eth.chain_id
            print(Fore.BLUE + f"🪫  Connected to BeanSwap RPC: {url}\n")
            return w3_instance
        except Exception as e:
            print(Fore.RED + f"Failed to connect to {url}, trying another...")
    raise Exception(Fore.RED + "❌ Unable to connect")

def sleep(seconds):
    time.sleep(seconds)

def get_random_eth_amount(w3_instance):
    amount = random.uniform(0.0001, 0.01)
    return w3_instance.to_wei(round(amount, 6), "ether")

def swap_eth_for_tokens(w3_instance, account, token_address, amount_in_wei, token_symbol):
    router = w3_instance.eth.contract(
        address=Web3.to_checksum_address(ROUTER_CONTRACT),
        abi=ABI
    )
    try:
        print(Fore.GREEN + f"🔄 Swap {w3_instance.from_wei(amount_in_wei, 'ether')} MON > {token_symbol}")
        nonce = w3_instance.eth.get_transaction_count(account.address, "pending")
        deadline = int(time.time()) + 600
        tx = router.functions.swapExactETHForTokens(
            0,
            [Web3.to_checksum_address(WMON_CONTRACT), Web3.to_checksum_address(token_address)],
            account.address,
            deadline
        ).build_transaction({
            'from': account.address,
            'value': amount_in_wei,
            'gas': 210000,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gasPrice': w3_instance.eth.gas_price
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3_instance.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
    except Exception as e:
        print(Fore.RED + f"❌ Failed swap: {str(e)}")

def swap_tokens_for_eth(w3_instance, account, token_address, token_symbol):
    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]
    token_contract = w3_instance.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=erc20_abi
    )
    balance = token_contract.functions.balanceOf(account.address).call()
    if balance == 0:
        print(Fore.BLACK + f"❌ No balance {token_symbol}, skip")
        return
    router = w3_instance.eth.contract(
        address=Web3.to_checksum_address(ROUTER_CONTRACT),
        abi=ABI
    )
    try:
        print(Fore.GREEN + f"🔄 Swap {token_symbol} > MON")
        nonce = w3_instance.eth.get_transaction_count(account.address, "pending")
        approve_tx = token_contract.functions.approve(
            Web3.to_checksum_address(ROUTER_CONTRACT),
            balance
        ).build_transaction({
            'from': account.address,
            'gas': 100000,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gasPrice': w3_instance.eth.gas_price
        })
        signed_approve = account.sign_transaction(approve_tx)
        w3_instance.eth.send_raw_transaction(signed_approve.raw_transaction)
        nonce = w3_instance.eth.get_transaction_count(account.address, "pending")
        deadline = int(time.time()) + 600
        tx = router.functions.swapExactTokensForETH(
            balance,
            0,
            [Web3.to_checksum_address(token_address), Web3.to_checksum_address(WMON_CONTRACT)],
            account.address,
            deadline
        ).build_transaction({
            'from': account.address,
            'gas': 210000,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gasPrice': w3_instance.eth.gas_price
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3_instance.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
        delay_time = random.uniform(1, 3)
        print(Fore.LIGHTBLACK_EX + f"⏳ Wait {delay_time:.2f} seconds")
        sleep(delay_time)
    except Exception as e:
        print(Fore.RED + f"❌ Failed: {str(e)}")

def get_balance(w3_instance, account):
    mon_balance = w3_instance.eth.get_balance(account.address)
    print(Fore.GREEN + f"🧧 MON    : {w3_instance.from_wei(mon_balance, 'ether')} MON")
    erc20_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        }
    ]
    weth_contract = w3_instance.eth.contract(
        address=Web3.to_checksum_address(WMON_CONTRACT),
        abi=erc20_abi
    )
    weth_balance = weth_contract.functions.balanceOf(account.address).call()
    print(Fore.GREEN + f"🧧 WETH   : {w3_instance.from_wei(weth_balance, 'ether')} WETH")
    print(" ")

def main():
    w3_instance = connect_to_rpc()
    account = Account.from_key(PRIVATE_KEY)
    print(Fore.GREEN + f"🧧 Account: {account.address}\n")
    get_balance(w3_instance, account)
    for token_symbol, token_address in TOKEN_ADDRESSES.items():
        eth_amount = get_random_eth_amount(w3_instance)
        swap_eth_for_tokens(w3_instance, account, token_address, eth_amount, token_symbol)
        delay_time = random.uniform(1, 3)
        print(Fore.LIGHTBLACK_EX + f"⏳ Wait {delay_time:.2f} seconds")
        sleep(delay_time)
    print("\n" + Fore.WHITE + "🧿 All Token Swaps Completed\n")
    for token_symbol, token_address in TOKEN_ADDRESSES.items():
        swap_tokens_for_eth(w3_instance, account, token_address, token_symbol)

if __name__ == '__main__':
    main()
