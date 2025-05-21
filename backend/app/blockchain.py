from web3 import Web3
from flask import current_app
import json
import os

_web3 = None
_contract = None

def get_web3():
    global _web3
    if _web3 is None:
        _web3 = Web3(Web3.HTTPProvider(current_app.config['WEB3_PROVIDER']))
    return _web3

def get_contract():
    global _contract
    if _contract is None:
        web3 = get_web3()
        
        # Charger l'ABI du contrat
        contract_json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'build/contracts/TracabiliteAgricoleMaroc.json'
        )
        
        with open(contract_json_path, 'r') as f:
            contract_json = json.load(f)
        
        contract_abi = contract_json['abi']
        contract_address = current_app.config['CONTRACT_ADDRESS']
        
        _contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    
    return _contract