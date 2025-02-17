import os
import tempfile
import secrets
import base64
import requests
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Optional, List, Dict

class SecureFileProcessor:
    def __init__(self):
        self.AES_KEY = secrets.token_bytes(32)  # 256-bit AES key

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypts file content before processing."""
        nonce = secrets.token_bytes(12)  # Unique nonce
        aesgcm = AESGCM(self.AES_KEY)
        encrypted_data = aesgcm.encrypt(nonce, data, None)
        return nonce + encrypted_data

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypts file content before processing."""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        aesgcm = AESGCM(self.AES_KEY)
        return aesgcm.decrypt(nonce, ciphertext, None)

    @staticmethod
    def secure_temp_file(suffix: str = ".pdf") -> tempfile.NamedTemporaryFile:
        """Creates a secure temporary file."""
        return tempfile.NamedTemporaryFile(delete=True, suffix=suffix)

    def convert_pdf_to_image(self, pdf_data: bytes) -> Optional[str]:
        """Converts the first page of a PDF to an image for Donut processing."""
        try:
            with self.secure_temp_file(".pdf") as temp_pdf:
                temp_pdf.write(pdf_data)
                temp_pdf.flush()
                images = convert_from_path(temp_pdf.name)
            
            if images:
                with self.secure_temp_file(".jpg") as temp_img:
                    images[0].save(temp_img.name, format="JPEG")
                    temp_img.seek(0)
                    return base64.b64encode(temp_img.read()).decode("utf-8")
            return None
        except Exception as e:
            print(f"Error converting PDF to image: {str(e)}, type: {type(e)}, args: {e.args}")
            return None

    def extract_text_from_pdf(self, pdf_data: bytes) -> List[Dict]:
        """Extracts text and their positions from PDF."""
        text_elements = []
        try:
            with self.secure_temp_file(".pdf") as temp_pdf:
                temp_pdf.write(pdf_data)
                temp_pdf.flush()
                doc = fitz.open(temp_pdf.name)
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    words = page.get_text("words")
                    for word in words:
                        text_elements.append({
                            'text': word[4],
                            'bbox': word[:4],
                            'page': page_num
                        })
                return text_elements
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}, type: {type(e)}, args: {e.args}")
            return []

    def remove_pdf_metadata(self, pdf_data: bytes) -> bytes:
        """Removes metadata from a redacted PDF."""
        try:
            if not pdf_data:  # Check if pdf_data is empty
                print("Error: pdf_data is empty before metadata removal.")
            with self.secure_temp_file(".pdf") as temp_pdf:
                temp_pdf.write(pdf_data)
                temp_pdf.flush()
                doc = fitz.open(temp_pdf.name)
                doc.set_metadata({})

                with self.secure_temp_file("_secure.pdf") as secure_pdf:
                    doc.save(secure_pdf.name)
                    secure_pdf.seek(0)
                    return secure_pdf.read()
        except Exception as e:
            print(f"Error removing PDF metadata: {str(e)}")
            return pdf_data