#!/usr/bin/env python3
import os
import sys
import time
from dotenv import load_dotenv
from web3 import Web3
from colorama import init, Fore

init(autoreset=True)

def displayHeader():
    print(Fore.BLUE + "====================")
    print(Fore.BLUE + "   MONORAIL Bot     ")
    print(Fore.BLUE + "====================")

load_dotenv()
displayHeader()

RPC_URL = "https://testnet-rpc.monad.xyz"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"
CONTRACT_ADDRESS = "0xC995498c22a012353FAE7eCC701810D673E25794"
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    print(Fore.RED + "❌ Private key tidak ditemukan! Set dalam .env file.")
    sys.exit(1)
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
print(Fore.BLUE + "💨  Starting Monorail 🚀🚀🚀🚀")
print(" ")
print(Fore.GREEN + f"✅ Wallet initialized: {account.address}")

def checkBalance():
    balance = w3.eth.get_balance(account.address)
    print(Fore.CYAN + f"💰 Balance: {w3.from_wei(balance, 'ether')} ETH")
    if balance < w3.to_wei(0.1, 'ether'):
        print(Fore.RED + "❌ Saldo tidak cukup untuk transaksi.")
        sys.exit(1)

def sendTransaction():
    checkBalance()
    walletData = { "account": { "address": account.address } }
    data = (
        "0x96f25cbe0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e0590015a873bf326bd645c3e1266d4db41c4e6b000000000000000000000000000000000000000000000000016345785d8a0000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000"
        + account.address[2:]
        + "000000000000000000000000000000000000000000000000542f8f7c3d64ce470000000000000000000000000000000000000000000000000000002885eeed340000000000000000000000000000000000000000000000000000000000000004000000000000000000000000760afe86e5de5fa0ee542fc7b7b713e1c5425701000000000000000000000000760afe86e5de5fa0ee542fc7b7b713e1c5425701000000000000000000000000cba6b9a951749b8735c603e7ffc5151849248772000000000000000000000000760afe86e5de5fa0ee542fc7b7b713e1c54257010000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000014000000000000000000000000000000000000000000000000000000000000002800000000000000000000000000000000000000000000000000000000000000004d0e30db0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b3000000000000000000000000cba6b9a951749b8735c603e7ffc5151849248772000000000000000000000000000000000000000000000000016345785d8a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010438ed1739000000000000000000000000000000000000000000000000016345785d8a0000000000000000000000000000000000000000000000000000542f8f7c3d64ce4700000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000c995498c22a012353fae7ecc701810d673e257940000000000000000000000000000000000000000000000000000002885eeed340000000000000000000000000000000000000000000000000000000000000002000000000000000000000000760afe86e5de5fa0ee542fc7b7b713e1c5425701000000000000000000000000e0590015a873bf326bd645c3e1266d4db41c4e6b000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044095ea7b3000000000000000000000000cba6b9a951749b8735c603e7ffc5151849248772000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    )
    value = w3.to_wei(0.1, 'ether')
    try:
        print(Fore.YELLOW + "🔍 Memeriksa apakah transaksi bisa dieksekusi...")
        # Simulasikan panggilan (eth_call)
        w3.eth.call({'to': CONTRACT_ADDRESS, 'data': data})
        print(Fore.GREEN + "✅ Transaksi valid. Melanjutkan...")
        try:
            gasLimit = w3.eth.estimate_gas({
                'from': account.address,
                'to': CONTRACT_ADDRESS,
                'value': value,
                'data': data
            })
        except Exception as err:
            print(Fore.YELLOW + "⚠️ Estimasi gas gagal. Menggunakan gas limit default.")
            gasLimit = 500000
        tx = {
            'from': account.address,
            'to': CONTRACT_ADDRESS,
            'data': data,
            'value': value,
            'gas': gasLimit,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address)
        }
        print(Fore.BLUE + "🚀 Mengirim transaksi...")
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.GREEN + "✅ Transaksi dikirim! Menunggu konfirmasi...")
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(Fore.GREEN + "🎉 Transaksi sukses!")
        print(Fore.CYAN + f"🔗 Explorer: {EXPLORER_URL}{tx_hash.hex()}")
    except Exception as error:
        print(Fore.RED + "❌ Error terjadi: " + str(error))

if __name__ == '__main__':
    sendTransaction()
