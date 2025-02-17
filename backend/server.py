from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pii_redactor import PIIRedactor
import io
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for the extension

redactor = PIIRedactor()

@app.route('/redact', methods=['POST'])
def redact_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        pii_filters = request.form.getlist('filters')

        if not file or not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Invalid file format. Please upload a PDF.'}), 400

        # Read and encrypt the uploaded file
        file_data = file.read()
        encrypted_data = redactor.file_processor.encrypt_data(file_data)

        # Process the document
        result = redactor.process_document(encrypted_data, pii_filters)

        if result is None:
            return jsonify({'error': 'Processing failed'}), 500

        # Send the redacted file back
        return send_file(
            io.BytesIO(result),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='redacted_document.pdf'
        )

    except Exception as e:
        return jsonify({'error': str(e), 'type': str(type(e)), 'args': str(e.args)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7678, debug=True)  # Enable debug mode
