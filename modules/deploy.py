#!/usr/bin/env python3
import os, sys, time, random
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_standard, install_solc
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = "https://testnet-rpc.monad.xyz"

if not PRIVATE_KEY or not RPC_URL:
    print(Fore.RED + "? PRIVATE_KEY atau RPC_URL tidak ditemukan di .env")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Nama acak berdasarkan kata kimia dan planet
chemical_terms = ["Atom", "Molecule", "Ion", "Enzyme", "Catalyst", "Plasma", "Acid", "Base", "Bond", "Protein"]
planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Neptune", "Pluto", "Europa", "Titan", "Charon"]

def generate_random_name():
    return random.choice(chemical_terms) + random.choice(planets) + str(random.randint(1, 9999))

# Kontrak Solidity
contract_source = '''
pragma solidity ^0.8.0;

contract Counter {
    uint256 private count;

    event CountIncremented(uint256 newCount);

    function increment() public {
        count += 1;
        emit CountIncremented(count);
    }

    function getCount() public view returns (uint256) {
        return count;
    }
}
'''

def compile_contract():
    print(Fore.YELLOW + "?? Compiling contract...")
    install_solc("0.8.0")
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {"Counter.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode"]}
            }
        }
    }, solc_version="0.8.0")

    contract_data = compiled['contracts']['Counter.sol']['Counter']
    abi = contract_data['abi']
    bytecode = contract_data['evm']['bytecode']['object']
    print(Fore.GREEN + "? Compilation successful!")
    return abi, bytecode

def deploy_contract(name):
    abi, bytecode = compile_contract()
    nonce = w3.eth.get_transaction_count(account.address)
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    print(Fore.BLUE + f"?? Deploying contract: {name}")
    
    try:
        tx = Contract.constructor().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 3000000,
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(Fore.LIGHTBLACK_EX + "? Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            print(Fore.RED + "? Deployment failed!")
        else:
            print(Fore.GREEN + f"? Contract {name} deployed successfully!")
            print(Fore.CYAN + f"?? Address: {receipt.contractAddress}")
            print(Fore.CYAN + f"?? Tx Hash: {tx_hash.hex()}")
            return receipt.contractAddress
    except Exception as e:
        print(Fore.RED + f"? Error: {str(e)}")

def main():
    print(Fore.MAGENTA + Style.BRIGHT + "?? Starting Contract Deployment...\n")
    total = 5

    for i in range(total):
        contract_name = generate_random_name()
        print(Fore.YELLOW + f"?? Deploying ({i+1}/{total}): {contract_name}")
        deploy_contract(contract_name)
        delay = random.randint(4000, 6000) / 1000  # seconds
        print(Fore.LIGHTBLACK_EX + f"?? Waiting {delay:.2f} seconds...\n")
        time.sleep(delay)

    print(Fore.GREEN + Style.BRIGHT + "?? All contracts deployed successfully!\n")

if __name__ == "__main__":
    main()
