#!/usr/bin/env python3
import os, sys, time, random, json
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_standard, install_solc
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = "https://testnet-rpc.monad.xyz"

if not PRIVATE_KEY or not RPC_URL:
    print(Fore.RED + "❌ Missing environment variables!")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

chemical_terms = [
    "Atom", "Molecule", "Electron", "Proton", "Neutron", "Ion", "Isotope", "Reaction", "Catalyst", "Solution",
    "Acid", "Base", "pH", "Oxidation", "Reduction", "Bond", "Valence", "Electrolyte", "Polymer", "Monomer",
    "Enzyme", "Substrate", "Covalent", "Ionic", "Metal", "Nonmetal", "Gas", "Liquid", "Solid", "Plasma",
    "Entropy", "Enthalpy", "Thermodynamics", "OrganicChemistry", "InorganicChemistry", "Biochemistry", "PhysicalChemistry", "Analytical", "Synthesis", "Decomposition",
    "Exothermic", "Endothermic", "Stoichiometry", "Concentration", "Molarity", "Molality", "Titration", "Indicator", "Chromatography", "Spectroscopy",
    "Electrochemistry", "GalvanicCell", "Electrolysis", "Anode", "Cathode", "Electrode", "Hydrolysis", "Hydrogenation", "Dehydrogenation", "Polymerization",
    "Depolymerization", "Catalyst", "Inhibitor", "Adsorption", "Absorption", "Diffusion", "Osmosis", "Colloid", "Suspension", "Emulsion",
    "Aerosol", "Surfactant", "Detergent", "Soap", "AminoAcid", "Protein", "Carbohydrate", "Lipid", "Nucleotide", "DNA",
    "RNA", "ActivationEnergy", "Complex", "Ligand", "Coordination", "Crystal", "Amorphous", "Isomer", "Stereochemistry"
]

planets = [
    "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Ceres",
    "Eris", "Haumea", "Makemake", "Ganymede", "Titan", "Callisto", "Io", "Europa", "Triton", "Charon",
    "Titania", "Oberon", "Rhea", "Iapetus", "Dione", "Tethys", "Enceladus", "Miranda", "Ariel", "Umbriel",
    "Proteus", "Nereid", "Phobos", "Deimos", "Amalthea", "Himalia", "Elara", "Pasiphae", "Sinope", "Lysithea",
    "Carme", "Ananke", "Leda", "Thebe", "Adrastea", "Metis", "Callirrhoe", "Themisto", "Megaclite", "Taygete",
    "Chaldene", "Harpalyke", "Kalyke", "Iocaste", "Erinome", "Isonoe", "Praxidike", "Autonoe", "Thyone", "Hermippe",
    "Aitne", "Eurydome", "Euanthe", "Euporie", "Orthosie", "Sponde", "Kale", "Pasithee", "Hegemone", "Mneme",
    "Aoede", "Thelxinoe", "Arche", "Kallichore", "Helike", "Carpo", "Eukelade", "Cyllene", "Kore", "Herse",
    "Dia", "S2003J2", "S2003J3", "S2003J4", "S2003J5", "S2003J9", "S2003J10", "S2003J12", "S2003J15"
]

def generate_random_name():
    combined_terms = chemical_terms + planets
    random.shuffle(combined_terms)
    return "".join(combined_terms[:3])

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
    print("Compiling contract...")
    install_solc('0.8.0')
    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {"Counter.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        }
    }, solc_version="0.8.0")
    contract_data = compiled_sol['contracts']['Counter.sol']['Counter']
    abi = contract_data['abi']
    bytecode = contract_data['evm']['bytecode']['object']
    print(Fore.GREEN + "Contract compiled successfully!")
    return abi, bytecode

def deploy_contract(contract_name):
    abi, bytecode = compile_contract()
    print(Fore.BLUE + f"Deploying contract {contract_name} to blockchain...")
    try:
        nonce = w3.eth.get_transaction_count(account.address)
        print(Fore.LIGHTBLACK_EX + f"Using nonce: {nonce}")
        Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        tx = Contract.constructor().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 3000000,
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print("⏳ Waiting for transaction confirmation...")
        w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt is None or receipt.status != 1:
            print(Fore.RED + "Deployment failed!")
            sys.exit(1)
        else:
            print(Fore.GREEN + f"Contract {contract_name} deployed successfully!")
            print(Fore.CYAN + f"\n📌 Contract Address: {receipt.contractAddress}")
            print(Fore.CYAN + f"\n📜 Transaction Hash: {tx_hash.hex()}")
            print(Fore.GREEN + "\n✅ Deployment complete! 🎉\n")
    except Exception as e:
        print(Fore.RED + f"Deployment failed! {str(e)}")
        sys.exit(1)

def main():
    print(Fore.BLUE + "🚀 Starting Deploy Contract ©©©©")
    print(" ")
    number_of_contracts = 5
    for i in range(number_of_contracts):
        contract_name = generate_random_name()
        print(Fore.YELLOW + f"\n🔨 Deploying contract {i+1}/{number_of_contracts}: {contract_name}")
        deploy_contract(contract_name)
        delay_seconds = random.randint(4000, 6000) / 1000
        print(Fore.LIGHTBLACK_EX + f"⏳ Waiting for {delay_seconds} Seconds")
        time.sleep(delay_seconds)
    print(Fore.GREEN + Style.BRIGHT + "\n✅ All contracts deployed successfully! 🎉\n")
    sys.exit(0)

if __name__ == '__main__':
    main()
