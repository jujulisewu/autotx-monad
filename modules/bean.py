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

RPC_URLS = ["https://testnet-rpc.monad.xyz"]
CHAIN_ID = 10143

ROUTER_CONTRACT = "0xCa810D095e90Daae6e867c19DF6D9A8C56db2c89"
WMON_CONTRACT = "0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701"
USDC_CONTRACT = "0xf817257fed379853cDe0fa4F97AB987181B1E5Ea"
BEAN_CONTRACT = "0x268E4E24E0051EC27b3D27A95977E71cE6875a05"
JAI_CONTRACT  = "0x70F893f65E3C1d7f82aad72f71615eb220b74D10"

TOKEN_ADDRESSES = {
    "USDC": USDC_CONTRACT,
    "BEAN": BEAN_CONTRACT,
    "JAI": JAI_CONTRACT
}

ABI_URL = "https://raw.githubusercontent.com/shareithub/autotx-monad/refs/heads/main/abi/BEAN.js"

def fetch_abi(url):
    try:
        print(Fore.YELLOW + f"?? Mengunduh ABI dari {url}...")
        response = requests.get(url)
        response.raise_for_status()
        abi_content = response.text.strip()

        abi_match = re.search(r'const\s+ABI\s*=\s*(\[.*\]);?', abi_content, re.DOTALL)
        if not abi_match:
            raise ValueError("Format ABI tidak valid!")

        abi_json_str = abi_match.group(1)
        abi_json = json.loads(abi_json_str)

        print(Fore.GREEN + "? ABI berhasil diunduh dan diproses!\n")
        return abi_json
    except Exception as e:
        raise Exception(Fore.RED + f"? Gagal mengunduh ABI: {str(e)}")

ABI = fetch_abi(ABI_URL)

def connect_to_rpc():
    for url in RPC_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(url))
            _ = w3.eth.chain_id
            print(Fore.BLUE + f"?? Connected to RPC: {url}\n")
            return w3
        except Exception as e:
            print(Fore.RED + f"Gagal konek {url}, mencoba lainnya...")
    raise Exception(Fore.RED + "? Semua RPC gagal")

def sleep(seconds):
    time.sleep(seconds)

def get_random_eth_amount(w3):
    amount = random.uniform(0.001, 0.01)
    return w3.to_wei(round(amount, 6), "ether")

def swap_eth_for_tokens(w3, account, token_address, amount_in_wei, token_symbol):
    router = w3.eth.contract(address=Web3.to_checksum_address(ROUTER_CONTRACT), abi=ABI)
    try:
        gas_price = w3.eth.gas_price
        gas_limit = 210000
        total_cost = amount_in_wei + (gas_price * gas_limit)
        balance = w3.eth.get_balance(account.address)

        if balance < total_cost:
            print(Fore.RED + f"? Skip {token_symbol}: saldo tidak cukup untuk swap + gas.")
            return

        print(Fore.GREEN + f"?? Swap {w3.from_wei(amount_in_wei, 'ether')} MON ? {token_symbol}")
        nonce = w3.eth.get_transaction_count(account.address, "pending")
        deadline = int(time.time()) + 600

        tx = router.functions.swapExactETHForTokens(
            0,
            [Web3.to_checksum_address(WMON_CONTRACT), Web3.to_checksum_address(token_address)],
            account.address,
            deadline
        ).build_transaction({
            'from': account.address,
            'value': amount_in_wei,
            'gas': gas_limit,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gasPrice': gas_price
        })

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.YELLOW + f"?? TX Hash: {tx_hash.hex()}")
    except Exception as e:
        print(Fore.RED + f"? Gagal swap {token_symbol}: {str(e)}")

def swap_tokens_for_eth(w3, account, token_address, token_symbol):
    erc20_abi = [
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
    ]
    token = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
    balance = token.functions.balanceOf(account.address).call()
    if balance == 0:
        print(Fore.BLACK + f"?? Tidak ada saldo {token_symbol}, lewati")
        return

    router = w3.eth.contract(address=Web3.to_checksum_address(ROUTER_CONTRACT), abi=ABI)
    try:
        print(Fore.GREEN + f"?? Swap {token_symbol} ? MON")
        nonce = w3.eth.get_transaction_count(account.address, "pending")
        gas_price = w3.eth.gas_price

        # Approve
        approve_tx = token.functions.approve(Web3.to_checksum_address(ROUTER_CONTRACT), balance).build_transaction({
            'from': account.address,
            'gas': 100000,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gasPrice': gas_price
        })
        signed_approve = account.sign_transaction(approve_tx)
        w3.eth.send_raw_transaction(signed_approve.raw_transaction)

        nonce = w3.eth.get_transaction_count(account.address, "pending")
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
            'gasPrice': gas_price
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.YELLOW + f"?? TX Hash: {tx_hash.hex()}")
        sleep(random.uniform(1, 3))
    except Exception as e:
        print(Fore.RED + f"? Gagal swap balik {token_symbol}: {str(e)}")

def get_balance(w3, account):
    mon = w3.eth.get_balance(account.address)
    print(Fore.GREEN + f"?? MON    : {w3.from_wei(mon, 'ether')} MON")
    erc20_abi = [{"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}]
    weth = w3.eth.contract(address=Web3.to_checksum_address(WMON_CONTRACT), abi=erc20_abi)
    wmon_balance = weth.functions.balanceOf(account.address).call()
    print(Fore.GREEN + f"?? WMON   : {w3.from_wei(wmon_balance, 'ether')} WMON\n")

def main():
    w3 = connect_to_rpc()
    account = Account.from_key(PRIVATE_KEY)
    print(Fore.GREEN + f"?? Account: {account.address}\n")
    get_balance(w3, account)

    # SWAP ETH TO TOKEN
    for symbol, address in TOKEN_ADDRESSES.items():
        eth_amount = get_random_eth_amount(w3)
        swap_eth_for_tokens(w3, account, address, eth_amount, symbol)
        sleep(random.uniform(1, 3))

    print("\n" + Fore.WHITE + "? Semua Swap ke Token Selesai\n")

    # SWAP TOKEN TO ETH
    for symbol, address in TOKEN_ADDRESSES.items():
        swap_tokens_for_eth(w3, account, address, symbol)

if __name__ == '__main__':
    main()
