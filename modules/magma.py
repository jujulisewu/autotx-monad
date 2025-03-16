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

def displayHeader():
    print(Fore.BLUE + "====================")
    print(Fore.BLUE + "     MAGMA Bot      ")
    print(Fore.BLUE + "====================")

displayHeader()

RPC_URL = "https://testnet-rpc.monad.xyz"
EXPLORER_URL = "https://testnet.monadexplorer.com/tx/"
w3 = Web3(Web3.HTTPProvider(RPC_URL))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    print(Fore.RED + "❌ Private key tidak ditemukan di .env")
    sys.exit(1)
account = w3.eth.account.from_key(PRIVATE_KEY)

contractAddress = "0x2c9C959516e9AAEdB2C748224a41249202ca8BE7"
gasLimitStake = 500000
gasLimitUnstake = 800000

def getRandomAmount():
    min_val = 0.01
    max_val = 0.05
    randomAmount = random.uniform(min_val, max_val)
    # Bulatkan hingga 4 desimal, kemudian konversi ke Wei
    return w3.to_wei(round(randomAmount, 4), 'ether')

def delay(ms):
    time.sleep(ms / 1000)

def stakeMON():
    try:
        stakeAmount = getRandomAmount()
        print(Fore.BLUE + "🪫  Starting Magma ⏩⏩⏩⏩")
        print(" ")
        print(Fore.MAGENTA + f"🔄 Magma stake: {w3.from_wei(stakeAmount, 'ether')} MON")
        tx = {
            'to': contractAddress,
            'data': "0xd5575982",
            'gas': gasLimitStake,
            'value': stakeAmount,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price
        }
        print(Fore.GREEN + "🔄 STAKE")
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.YELLOW + f"➡️  Hash: {tx_hash.hex()}")
        print(Fore.GREEN + "🔄 Wait Confirmation")
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(Fore.GREEN + "✅ Stake DONE")
        return stakeAmount
    except Exception as error:
        print(Fore.RED + f"❌ Staking failed: {error}")
        raise error

def unstakeGMON(amountToUnstake):
    try:
        print(Fore.GREEN + f"🔄 Unstake: {w3.from_wei(amountToUnstake, 'ether')} gMON")
        functionSelector = "0x6fed1ea7"
        paddedAmount = amountToUnstake.to_bytes(32, byteorder='big').hex()
        data = functionSelector + paddedAmount
        tx = {
            'to': contractAddress,
            'data': data,
            'gas': gasLimitUnstake,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price
        }
        print(Fore.RED + "🔄 Unstake")
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.YELLOW + f"➡️ Hash: {tx_hash.hex()}")
        print(Fore.GREEN + "🔄 Wait Confirmation")
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(Fore.GREEN + "✅ Unstake DONE")
    except Exception as error:
        print(Fore.RED + f"❌ Unstaking failed: {error}")
        raise error

def runAutoCycle():
    try:
        stakeAmount = stakeMON()
        print(Fore.YELLOW + "🔄 wait")
        delay(73383)
        unstakeGMON(stakeAmount)
    except Exception as error:
        print(Fore.RED + f"❌ Failed: {error}")

if __name__ == '__main__':
    runAutoCycle()
