import hashlib
import json
import time

# Block class to store certificate data
class Block:
    def __init__(self, index, certificate_data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.certificate_data = certificate_data  # Certificate details (e.g., certificate ID)
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    # Method to calculate the block's hash
    def calculate_hash(self):
        # Combine block data and calculate hash
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

# Blockchain class to manage the chain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()  # Create the first block (genesis block)
    
    # Create the first block (genesis block)
    def create_genesis_block(self):
        genesis_block = Block(0, "Genesis Block", "0")
        self.chain.append(genesis_block)

    # Add a new block to the blockchain
    def add_block(self, certificate_data):
        last_block = self.chain[-1]
        new_block = Block(len(self.chain), certificate_data, last_block.hash)
        self.chain.append(new_block)

    # Check the blockchain's integrity by comparing hashes
    def check_integrity(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # If the current block's hash doesn't match or previous hash doesn't match
            if current_block.hash != current_block.calculate_hash() or current_block.previous_hash != previous_block.hash:
                return False
        return True