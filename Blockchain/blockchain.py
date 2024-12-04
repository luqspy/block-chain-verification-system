import hashlib
import json
import time

# Block class to store certificate data
class Block:
    def __init__(self, index, certificate_data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.certificate_data = certificate_data  # Certificate details (e.g., certificate ID, department, and hash)
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
        # The genesis block (initial block) does not have valid certificate data
        genesis_block = Block(0, {"certificate_id": "0", "department": "Genesis", "pdf_hash": "0"}, "0")
        self.chain.append(genesis_block)

    # Add a new block to the blockchain
    def add_block(self, certificate_data):
        # Get the last block to ensure the blockchain is connected
        last_block = self.chain[-1]
        new_block = Block(len(self.chain), certificate_data, last_block.hash)
        self.chain.append(new_block)

    # Verify a certificate by its ID and hash
    def verify_certificate(self, certificate_id, pdf_hash):
        # Search for the certificate by ID and check if the hash matches
        certificate = self.get_certificate_by_id(certificate_id)
        if certificate and certificate['pdf_hash'] == pdf_hash:
            return True
        return False

    # Retrieve certificate data by its ID
    def get_certificate_by_id(self, certificate_id):
        # Loop through the blockchain and check for the certificate with the matching ID
        for block in self.chain:
            if block.certificate_data['certificate_id'] == certificate_id:
                return block.certificate_data
        return None  # Return None if certificate not found

    # Check the blockchain's integrity by comparing hashes
    def check_integrity(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # If the current block's hash doesn't match or previous hash doesn't match
            if current_block.hash != current_block.calculate_hash() or current_block.previous_hash != previous_block.hash:
                return False
        return True

    # Method to add a certificate to the blockchain
    def add_certificate(self, department, certificate_id, pdf_hash):
        certificate_data = {
            "certificate_id": certificate_id,
            "department": department,
            "pdf_hash": pdf_hash
        }
        self.add_block(certificate_data)

    # Method to get all certificates (for admin or other purposes)
    def get_all_certificates(self):
        certificates = []
        for block in self.chain:
            certificates.append(block.certificate_data)
        return certificates

