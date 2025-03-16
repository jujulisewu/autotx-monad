#!/usr/bin/env python3
import os
import sys
import time
import random
import json
from dotenv import load_dotenv
from web3 import Web3
from colorama import init, Fore, Style

# Inisialisasi colorama dan load .env
init(autoreset=True)
load_dotenv()

def display_header():
    print(Style.BRIGHT + Fore.CYAN + "======================================")
    print(Style.BRIGHT + Fore.CYAN + "            UNISWAP Bot               ")
    print(Style.BRIGHT + Fore.CYAN + "====================================\n")

display_header()

# Baca PRIVATE_KEY dari .env
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise Exception("No PRIVATE_KEY in .env")

RPC_URLS = [
    "https://testnet-rpc.monad.xyz"
]

CHAIN_ID = 10143
UNISWAP_V2_ROUTER_ADDRESS = Web3.to_checksum_address("0xCa810D095e90Daae6e867c19DF6D9A8C56db2c89")
WETH_ADDRESS = Web3.to_checksum_address("0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701")

# Token addresses dalam format checksum
TOKEN_ADDRESSES = {
    "DAC": Web3.to_checksum_address("0x0f0bdebf0f83cd1ee3974779bcb7315f9808c714"),
    "USDT": Web3.to_checksum_address("0x88b8e2161dedc77ef4ab7585569d2415a1c1055d"),
    "WETH": Web3.to_checksum_address("0x836047a99e11f376522b447bffb6e3495dd0637c"),
    "MUK": Web3.to_checksum_address("0x989d38aeed8408452f0273c7d4a17fef20878e62"),
    "USDC": Web3.to_checksum_address("0xf817257fed379853cDe0fa4F97AB987181B1E5Ea"),
    "CHOG": Web3.to_checksum_address("0xE0590015A873bF326bd645c3E1266d4db41C4E6B")
}

# Minimal ABI untuk ERC20 (balanceOf dan approve)
erc20Abi = [
    { "constant": True, "inputs": [{"name": "_owner", "type": "address"}],
      "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function" },
    { "constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}],
      "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function" }
]

# Minimal ABI untuk router (swapExactETHForTokens & swapExactTokensForETH)
routerAbi = [
    {
        "name": "swapExactETHForTokens",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            { "internalType": "uint256", "name": "amountOutMin", "type": "uint256" },
            { "internalType": "address[]", "name": "path", "type": "address[]" },
            { "internalType": "address", "name": "to", "type": "address" },
            { "internalType": "uint256", "name": "deadline", "type": "uint256" }
        ],
        "outputs": [
            { "internalType": "uint256[]", "name": "amounts", "type": "uint256[]" }
        ]
    },
    {
        "name": "swapExactTokensForETH",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            { "internalType": "uint256", "name": "amountIn", "type": "uint256" },
            { "internalType": "uint256", "name": "amountOutMin", "type": "uint256" },
            { "internalType": "address[]", "name": "path", "type": "address[]" },
            { "internalType": "address", "name": "to", "type": "address" },
            { "internalType": "uint256", "name": "deadline", "type": "uint256" }
        ],
        "outputs": [
            { "internalType": "uint256[]", "name": "amounts", "type": "uint256[]" }
        ]
    }
]

def connect_to_rpc():
    for url in RPC_URLS:
        try:
            provider = Web3(Web3.HTTPProvider(url))
            # Cek koneksi sederhana dengan mengambil network ID
            _ = provider.net.version
            print(Fore.BLUE + "🪫  Starting Uniswap ⏩⏩⏩⏩")
            return provider
        except Exception as e:
            print(Fore.RED + f"Failed to connect to {url}, trying another...")
    raise Exception("❌ Unable to connect to any RPC")

w3 = connect_to_rpc()

# Buat objek wallet dari PRIVATE_KEY
wallet = w3.eth.account.from_key(PRIVATE_KEY)
print(Fore.GREEN + f"🧧 Account: {wallet.address}")

def get_random_eth_amount():
    # Menghasilkan nilai acak antara 0.0001 dan 0.01 ether
    amount = random.uniform(0.0001, 0.01)
    # Bulatkan ke 6 desimal dan konversi ke wei
    return w3.to_wei(round(amount, 6), 'ether')

def get_balance():
    balance = w3.eth.get_balance(wallet.address)
    print(Fore.GREEN + f"🧧 MON: {w3.from_wei(balance, 'ether')} MON")
    # Dapatkan saldo WETH dari kontrak ERC20
    weth_contract = w3.eth.contract(address=WETH_ADDRESS, abi=erc20Abi)
    weth_balance = weth_contract.functions.balanceOf(wallet.address).call()
    print(Fore.GREEN + f"🧧 WETH: {w3.from_wei(weth_balance, 'ether')} WETH\n")

def swap_eth_for_tokens(tokenAddress, tokenSymbol, amountInWei):
    router = w3.eth.contract(address=UNISWAP_V2_ROUTER_ADDRESS, abi=routerAbi)
    try:
        print(Fore.GREEN + f"🔄 Swap {w3.from_wei(amountInWei, 'ether')} MON > {tokenSymbol}")
        nonce = w3.eth.get_transaction_count(wallet.address, "pending")
        deadline = int(time.time()) + 600  # 10 menit
        tx = router.functions.swapExactETHForTokens(
            0,
            [WETH_ADDRESS, tokenAddress],
            wallet.address,
            deadline
        ).build_transaction({
            'from': wallet.address,
            'value': amountInWei,
            'gas': 210000,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = wallet.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
    except Exception as e:
        print(Fore.RED + f"❌ Failed swap: {str(e)}")

def swap_tokens_for_eth(tokenAddress, tokenSymbol):
    token_contract = w3.eth.contract(address=tokenAddress, abi=erc20Abi)
    balance = token_contract.functions.balanceOf(wallet.address).call()
    if balance == 0:
        print(Fore.BLACK + f"❌ No balance {tokenSymbol}, skip")
        return
    router = w3.eth.contract(address=UNISWAP_V2_ROUTER_ADDRESS, abi=routerAbi)
    try:
        print(Fore.GREEN + f"🔄 Swap {tokenSymbol} > MON")
        # Approve router untuk menghabiskan token
        approve_tx = token_contract.functions.approve(UNISWAP_V2_ROUTER_ADDRESS, balance).build_transaction({
            'from': wallet.address,
            'gas': 100000,
            'nonce': w3.eth.get_transaction_count(wallet.address)
        })
        signed_approve_tx = wallet.sign_transaction(approve_tx)
        w3.eth.send_raw_transaction(signed_approve_tx.raw_transaction)
        nonce = w3.eth.get_transaction_count(wallet.address, "pending")
        deadline = int(time.time()) + 600
        tx = router.functions.swapExactTokensForETH(
            balance,
            0,
            [tokenAddress, WETH_ADDRESS],
            wallet.address,
            deadline
        ).build_transaction({
            'from': wallet.address,
            'gas': 210000,
            'nonce': nonce,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = wallet.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
        delay = random.randint(1000, 3000)
        print(Fore.LIGHTBLACK_EX + f"⏳ Wait {delay/1000} seconds")
        time.sleep(delay / 1000)
    except Exception as e:
        print(Fore.RED + f"❌ Failed: {str(e)}")

def main():
    get_balance()
    # Swap ETH to tokens
    for tokenSymbol, tokenAddress in TOKEN_ADDRESSES.items():
        ethAmount = get_random_eth_amount()
        swap_eth_for_tokens(tokenAddress, tokenSymbol, ethAmount)
        delay = random.randint(1000, 3000)
        print(Fore.LIGHTBLACK_EX + f"⏳ Wait {delay/1000} seconds")
        time.sleep(delay / 1000)
    print("\n" + Fore.WHITE + "🧿 All Token Reverse to MONAD\n")
    # Swap tokens back to ETH
    for tokenSymbol, tokenAddress in TOKEN_ADDRESSES.items():
        swap_tokens_for_eth(tokenAddress, tokenSymbol)

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(Fore.RED + f"❌ Error: {err}")
