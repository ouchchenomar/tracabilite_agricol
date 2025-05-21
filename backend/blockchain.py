import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict

class Block:
    def __init__(self, index: int, data: Dict, timestamp: float, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, {"message": "Genesis Block"}, time.time(), "0")
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Dict) -> Block:
        previous_block = self.get_latest_block()
        new_block = Block(
            previous_block.index + 1,
            data,
            time.time(),
            previous_block.hash
        )
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_block_data(self, index: int) -> Dict:
        if 0 <= index < len(self.chain):
            return self.chain[index].data
        return None

    def get_all_data(self) -> List[Dict]:
        return [block.data for block in self.chain[1:]]  # Exclude genesis block

class DataSecurity:
    def __init__(self):
        self.blockchain = Blockchain()

    def secure_data(self, data: Dict) -> str:
        """
        Sécurise les données en les ajoutant à la blockchain
        Retourne l'hash du bloc créé
        """
        block = self.blockchain.add_block(data)
        return block.hash

    def verify_data(self, data_hash: str) -> bool:
        """
        Vérifie si les données existent dans la blockchain
        """
        for block in self.blockchain.chain:
            if block.hash == data_hash:
                return True
        return False

    def get_data_history(self) -> List[Dict]:
        """
        Retourne l'historique complet des données
        """
        return self.blockchain.get_all_data()

    def is_valid(self) -> bool:
        """
        Vérifie l'intégrité de la blockchain
        """
        return self.blockchain.is_chain_valid() 