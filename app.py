from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
import re
from parsers.text_cleaner import clean_rtf_text, deduplicate_list
from parsers.assembly_parser import parse_assembly_letter

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ADD THIS FUNCTION - It extracts text from PDF files
def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from {filepath}: {str(e)}")
        return ""
    return text

def parse_scope_of_work(text):
    """Parse Scope of Work document"""
    text = clean_rtf_text(text)
    
    materials = []
    material_patterns = [
        r'(?i)materials?:\s*([^\n]+)',
        r'(?i)product[s]?:\s*([^\n]+)',
    ]
    
    for pattern in material_patterns:
        matches = re.findall(pattern, text)
        materials.extend(matches)
    
    materials = deduplicate_list(materials)
    
    requirements = []
    req_patterns = [
        r'(?i)requirement[s]?:\s*([^\n]+)',
        r'(?i)shall\s+([^\n]+)',
    ]
    
    for pattern in req_patterns:
        matches = re.findall(pattern, text)
        requirements.extend(matches)
    
    requirements = deduplicate_list(requirements[:10])
    
    sentences = text.split('.')[:3]
    summary = '. '.join(sentences).strip()
    
    return {
        'summary': summary[:500] if summary else None,
        'materials': materials[:15] if materials else None,
        'requirements': requirements if requirements else None
    }

def parse_specification(text):
    """Parse Specification document"""
    manufacturers = []
    mfr_patterns = [
        r'(?i)manufacturer[s]?:\s*([^\n]+)',
        r'(?i)(?:Carlisle|GAF|Firestone|Johns Manville|Versico|Siplast|SOPREMA|Sika|Barrett|Tremco)',
    ]
    
    for pattern in mfr_patterns:
        matches = re.findall(pattern, text)
        manufacturers.extend(matches)
    
    manufacturers = deduplicate_list(manufacturers)
    
    products = []
    product_patterns = [
        r'(?i)product[s]?:\s*([^\n]+)',
        r'(?i)[A-Z][a-z]+\s+\d+\s*mil',
    ]
    
    for pattern in product_patterns:
        matches = re.findall(pattern, text)
        products.extend(matches)
    
    products = deduplicate_list(products)
    
    return {
        'manufacturers': manufacturers[:10] if manufacturers else None,
        'products': products[:15] if products else None
    }

def parse_drawing(text):
    """Parse Architectural Drawing"""
    elements = []
    element_patterns = [
        r'(?i)(?:roof|wall|parapet|drain|flashing|membrane)',
    ]
    
    for pattern in element_patterns:
        matches = re.findall(pattern, text)
        elements.extend(matches)
    
    elements = deduplicate_list(elements)
    
    callouts = re.findall(r'\d+[\.:]?\s+([A-Z][^\n]{10,50})', text)
    callouts = deduplicate_list(callouts)
    
    return {
        'elements': elements[:20] if elements else None,
        'callouts': callouts[:15] if callouts else None
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse_files():
    results = {
        'scope': None,
        'spec': None,
        'drawing': None,
        'assembly': None
    }
    
    for category in ['scope', 'spec', 'drawing', 'assembly']:
        if category in request.files:
            files = request.files.getlist(category)
            
            if category == 'assembly' and len(files) > 1:
                results['assembly'] = []
                for file in files:
                    if file and file.filename:
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                        file.save(filepath)
                        text = extract_text_from_pdf(filepath)
                        parsed = parse_assembly_letter(text)
                        parsed['filename'] = file.filename
                        results['assembly'].append(parsed)
            else:
                file = files[0] if files else None
                if file and file.filename:
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)
                    text = extract_text_from_pdf(filepath)
                    
                    if category == 'scope':
                        results['scope'] = parse_scope_of_work(text)
                    elif category == 'spec':
                        results['spec'] = parse_specification(text)
                    elif category == 'drawing':
                        results['drawing'] = parse_drawing(text)
                    elif category == 'assembly':
                        parsed = parse_assembly_letter(text)
                        parsed['filename'] = file.filename
                        results['assembly'] = parsed
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)