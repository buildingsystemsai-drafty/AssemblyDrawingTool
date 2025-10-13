import PyPDF2

def extract_text_from_pdf(filepath):
    """
    Extract text from PDF file
    """
    text = ""
    
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    
    except Exception as e:
        print(f"Error extracting text from {filepath}: {str(e)}")
        return ""
    
    return text