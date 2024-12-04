from flask import Flask, request, jsonify, render_template
import hashlib
from blockchain import Blockchain
import os

app = Flask(__name__)
blockchain = Blockchain()

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for the root URL (this renders the HTML page)
@app.route('/')
def home():
    return render_template("verify_certificate.html")  # Render the HTML file

# Route to add a new certificate (only accessible by government officials)
@app.route('/add_certificate', methods=['POST'])
def add_certificate():
    # Role-based access check (example: using a custom header or token)
    user_role = request.headers.get('Role')  # Example: 'Role: government'
    if user_role != 'government':
        return jsonify({"message": "Unauthorized to add certificates"}), 403
    
    certificate_id = request.form.get('certificate_id')
    department = request.form.get('department')  # Get department from form
    issuer = request.form.get('issuer')
    pdf_file = request.files['pdf_file']  # The uploaded PDF file

    # Save the PDF file temporarily
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
    pdf_file.save(pdf_path)

    # Generate hash of the PDF file
    pdf_hash = generate_pdf_hash(pdf_path)

    # Combine certificate metadata and PDF hash to add to blockchain
    certificate_data = {
        'certificate_id': certificate_id,
        'department': department,
        'issuer': issuer,
        'pdf_hash': pdf_hash  # Store the hash of the document
    }
    blockchain.add_certificate(department, certificate_id, pdf_hash)

    return jsonify({"message": "Certificate added successfully!"}), 201

# Route to verify certificate (by checking the hash)
@app.route('/verify_certificate', methods=['POST'])
def verify_certificate():
    certificate_id = request.form.get('certificate_id')
    department = request.form.get('department')  # Get department from form
    pdf_file = request.files.get('pdf_file')  # The uploaded PDF to verify

    if not certificate_id:
        return jsonify({"message": "Certificate ID is required!"}), 400

    if pdf_file:
        # Save the PDF file temporarily
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(pdf_path)

        # Generate hash of the uploaded PDF
        pdf_hash = generate_pdf_hash(pdf_path)

        # Verify the certificate with the given ID and hash
        if blockchain.verify_certificate(certificate_id, pdf_hash):
            return jsonify({"message": "Certificate is valid!"}), 200
        else:
            return jsonify({"message": "Certificate not found or invalid!"}), 404
    else:
        # Only verify by certificate ID if no PDF file is uploaded
        certificate_data = blockchain.get_certificate_by_id(certificate_id)
        if certificate_data:
            return jsonify({"message": "Certificate is valid!", "certificate": certificate_data}), 200
        else:
            return jsonify({"message": "Certificate not found!"}), 404

# Method to generate hash of the PDF
def generate_pdf_hash(pdf_path):
    sha256_hash = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Route to get certificates for a department (used for display)
@app.route('/get_certificates', methods=['GET'])
def get_certificates():
    # Fetch a list of all certificates (certificate_id and issuer) for display
    certificates = []
    for block in blockchain.chain:
        certificates.append({
            'certificate_id': block.certificate_data['certificate_id'],
            'issuer': block.certificate_data['issuer'],
            'department': block.certificate_data['department']
        })
    return jsonify(certificates)

if __name__ == '__main__':
    app.run(debug=True)
