from flask import Flask, request, jsonify
app = Flask(__name__)

# Initialize the blockchain
blockchain = Blockchain()

# Route to add a new certificate
@app.route('/add_certificate', methods=['POST'])
def add_certificate():
    certificate_id = request.json.get('certificate_id')
    issuer = request.json.get('issuer')
    certificate_data = f"{certificate_id} issued by {issuer}"
    blockchain.add_block(certificate_data)
    return jsonify({"message": "Certificate added successfully!"}), 201

# Route to check if certificate exists and verify integrity
@app.route('/verify_certificate', methods=['GET'])
def verify_certificate():
    certificate_id = request.args.get('certificate_id')
    for block in blockchain.chain:
        if certificate_id in block.certificate_data:
            return jsonify({"certificate_id": certificate_id, "status": "Valid", "block_data": block.__dict__}), 200
    return jsonify({"message": "Certificate not found!"}), 404

# Route to check blockchain integrity
@app.route('/check_integrity', methods=['GET'])
def check_integrity():
    if blockchain.check_integrity():
        return jsonify({"status": "Blockchain is intact!"}), 200
    else:
        return jsonify({"status": "Blockchain has been tampered!"}), 400

if __name__ == '__main__':
    app.run(debug=True)