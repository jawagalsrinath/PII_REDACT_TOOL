from typing import List, Dict
from file_processor import SecureFileProcessor
from models import query_donut  # Import query_donut from models.py
import fitz  # PyMuPDF

class PIIRedactor:
    def __init__(self):
        self.file_processor = SecureFileProcessor()

    def redact_pii(self, pdf_data: bytes, pii_filters: List[str]) -> bytes:
        """Redacts PII from a PDF using bounding boxes."""
        try:
            # First extract all text elements
            text_elements = self.file_processor.extract_text_from_pdf(pdf_data)
            
            # Convert first page to image for Donut processing
            image_base64 = self.file_processor.convert_pdf_to_image(pdf_data)
            if image_base64:
                donut_result = query_donut(image_base64)  # Use imported query_donut
                detected_pii = [
                    word for word in donut_result.get("text", "").split()
                    if any(pii_type in word.lower() for pii_type in pii_filters)
                ]
            else:
                detected_pii = []

            # Create temporary PDF and apply redactions
            with self.file_processor.secure_temp_file(".pdf") as temp_pdf:
                temp_pdf.write(pdf_data)
                temp_pdf.flush()
                doc = fitz.open(temp_pdf.name)

                for page_num in range(len(doc)):
                    page = doc[page_num]
                    
                    # Redact detected PII
                    for pii in detected_pii:
                        text_instances = page.search_for(pii)
                        for inst in text_instances:
                            page.add_redact_annot(inst, fill=(0, 0, 0))
                    
                    # Apply redactions
                    page.apply_redactions()

                # Save redacted PDF
                try:  # Add try block for save and read operations
                    with self.file_processor.secure_temp_file("_redacted.pdf") as redacted_pdf:
                        doc.save(redacted_pdf.name)
                        redacted_pdf.seek(0)
                        return redacted_pdf.read()
                except Exception as save_error:  # Catch errors during save/read
                    print(f"Error saving/reading redacted PDF: {str(save_error)}, type: {type(save_error)}, args: {save_error.args}")
                    return None  # Return None if save/read fails
        
        except Exception as e:
            print(f"Error during PII redaction: {str(e)}")
            return None

    def remove_metadata(self, pdf_data: bytes) -> bytes:
        """Removes metadata from a redacted PDF."""
        return self.file_processor.remove_pdf_metadata(pdf_data)

    def process_document(self, encrypted_pdf: bytes, pii_filters: List[str]) -> bytes:
        """Complete document processing pipeline."""
        try:
            # Decrypt the PDF
            decrypted_pdf = self.file_processor.decrypt_data(encrypted_pdf)
            
            # Perform redaction
            redacted_pdf = self.redact_pii(decrypted_pdf, pii_filters)
            if redacted_pdf is None or not redacted_pdf:  # Check if redacted_pdf is None or empty
                return None  # Return None if redaction failed or redacted_pdf is empty
            
            # Log redacted_pdf data before metadata removal
            if not redacted_pdf:  # Check if redacted_pdf is empty
                print("Error: redacted_pdf is empty before remove_metadata call.")
            
            # Remove metadata
            clean_pdf = self.remove_metadata(redacted_pdf)
            
            # Re-encrypt the result
            return self.file_processor.encrypt_data(clean_pdf)
            
        except Exception as e:
            print(f"Error in document processing: {str(e)}")
            return None