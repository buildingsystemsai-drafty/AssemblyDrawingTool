import pdfplumber
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(filepath):
    """
    Extract text from PDF file using pdfplumber for better accuracy.

    Args:
        filepath: Path to PDF file (string) or binary data (bytes)

    Returns:
        str: Extracted text from all pages
    """
    text = ""

    try:
        # Handle both file paths and binary data
        if isinstance(filepath, (str, bytes)):
            if isinstance(filepath, str):
                # File path provided
                with pdfplumber.open(filepath) as pdf:
                    logger.info(f"Extracting text from {filepath} ({len(pdf.pages)} pages)")

                    for i, page in enumerate(pdf.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            logger.debug(f"  Page {i}: {len(page_text)} chars")
                        else:
                            logger.warning(f"  Page {i}: No text (may need OCR)")
            else:
                # Binary data provided
                with pdfplumber.open(io.BytesIO(filepath)) as pdf:
                    logger.info(f"Extracting text from binary data ({len(pdf.pages)} pages)")

                    for i, page in enumerate(pdf.pages, 1):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        else:
                            logger.warning(f"  Page {i}: No text (may need OCR)")

    except Exception as e:
        logger.error(f"Error extracting text from {filepath}: {str(e)}")
        return ""

    return text