from flask import Flask, request, jsonify, render_template
import hashlib
import os
from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template("user_verification.html")  # Default page, for certificate verification

@app.route('/official')
def official_home():
    # Show upload page only for government officials
    user_role = request.headers.get('Role')  # For example, 'Role: government'
    if user_role != 'government':
        return jsonify({"message": "Unauthorized access. Only government officials can upload certificates."}), 403
    return render_template("official_upload.html")  # Page for uploading certificates

@app.route('/add_certificate', methods=['POST'])
def add_certificate():
    # Role-based check (Example: using custom headers or a token)
    user_role = request.headers.get('Role')  # Should be 'government' for officials
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

    # Add the certificate to the blockchain
    certificate_data = {
        'certificate_id': certificate_id,
        'department': department,
        'issuer': issuer,
        'pdf_hash': pdf_hash
    }
    blockchain.add_certificate(department, certificate_id, pdf_hash)

    return jsonify({"message": "Certificate added successfully!"}), 201

@app.route('/verify_certificate', methods=['POST'])
def verify_certificate():
    certificate_id = request.form.get('certificate_id')
    uploaded_file = request.files.get('pdf_file')

    # Verify by Certificate ID
    if certificate_id:
        certificate = blockchain.get_certificate_by_id(certificate_id)
        if certificate:
            return jsonify(certificate)
        else:
            return jsonify({"message": "Certificate not found"}), 404

    # Verify by uploading PDF file
    elif uploaded_file:
        file_hash = generate_pdf_hash(uploaded_file)
        certificate = blockchain.get_certificate_by_hash(file_hash)
        if certificate:
            return jsonify(certificate)
        else:
            return jsonify({"message": "Certificate not found"}), 404

    else:
        return jsonify({"message": "No certificate ID or file provided"}), 400


# Method to generate hash of the PDF
def generate_pdf_hash(pdf_path):
    sha256_hash = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == '__main__':
    app.run(debug=True)
