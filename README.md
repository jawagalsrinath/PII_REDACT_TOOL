# PII Redactor Extension

A secure web extension for redacting Personally Identifiable Information (PII) from PDF documents.

## Features

- Secure file handling with AES-GCM encryption
- AI-powered PII detection using Donut model
- Customizable redaction filters
- PDF processing with PyMuPDF
- Metadata removal for enhanced privacy

## Setup

1. Install the required Python packages:
```bash
pip install flask flask-cors PyMuPDF pdf2image cryptography requests
```

2. Set up your environment variables:
```bash
export HF_API_KEY=your_hugging_face_api_key
```

3. Start the backend server:
```bash
python backend/server.py
```

4. Load the extension in your browser:
   - Chrome: Go to `chrome://extensions/`
   - Enable Developer mode
   - Click "Load unpacked"
   - Select the extension directory

## Usage

1. Click the extension icon in your browser
2. Select the types of PII you want to redact
3. Choose a PDF file
4. Click "Redact Document"
5. The redacted PDF will be downloaded automatically

## Security Features

- AES-GCM encryption for file handling
- Secure temporary file management
- Metadata removal
- Memory-safe file processing

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.# PII_REDACT_TOOL
