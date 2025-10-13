from flask import Flask, render_template, request, jsonify
import os
import json
import sys
import PyPDF2
import re
from parsers.text_cleaner import clean_rtf_text, deduplicate_list
from parsers.assembly_parser import parse_assembly_letter
from parsers.arch_drawing_parser import parse_architectural_drawing
from parsers.spec_parser import SpecParser
from parsers.scope_parser import parse_scope

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_text_from_pdf(filepath):
    """Extract text from PDF file with better error handling"""
    text = ""
    try:
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"📄 Extracting {total_pages} pages from: {os.path.basename(filepath)}")
            
            for i, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                text += page_text + "\n"
                print(f"  ✓ Page {i}/{total_pages} - {len(page_text)} chars")
            
            print(f"  📊 Total extracted: {len(text)} characters")
    except Exception as e:
        print(f"❌ Error extracting text from {filepath}: {str(e)}")
        return ""
    return text

def safe_jsonify(data):
    """Safely convert data to JSON-serializable format"""
    if isinstance(data, dict):
        return {k: safe_jsonify(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [safe_jsonify(item) for item in data]
    elif isinstance(data, (str, int, float, bool, type(None))):
        return data
    else:
        return str(data)

# ============================================================================
# DOCUMENT PARSERS
# ============================================================================

def parse_scope_of_work(text):
    """Parse Scope of Work document"""
    print("\n" + "="*60)
    print("🔍 PARSING SCOPE OF WORK")
    print("="*60)
    
    text = clean_rtf_text(text)
    
    # Extract materials
    materials = []
    material_patterns = [
        r'(?i)materials?:\s*([^\n]+)',
        r'(?i)product[s]?:\s*([^\n]+)',
    ]
    
    for pattern in material_patterns:
        matches = re.findall(pattern, text)
        materials.extend(matches)
    
    materials = deduplicate_list(materials)
    print(f"  ✓ Found {len(materials)} materials")
    
    # Extract requirements
    requirements = []
    req_patterns = [
        r'(?i)requirement[s]?:\s*([^\n]+)',
        r'(?i)shall\s+([^\n]+)',
    ]
    
    for pattern in req_patterns:
        matches = re.findall(pattern, text)
        requirements.extend(matches)
    
    requirements = deduplicate_list(requirements[:10])
    print(f"  ✓ Found {len(requirements)} requirements")
    
    # Create summary
    sentences = text.split('.')[:3]
    summary = '. '.join(sentences).strip()
    print(f"  ✓ Generated summary ({len(summary)} chars)")
    
    result = {
        'summary': summary[:500] if summary else None,
        'materials': materials[:15] if materials else None,
        'requirements': requirements if requirements else None
    }
    
    print("="*60 + "\n")
    return result

def parse_specification(text):
    """Parse Specification document"""
    print("\n" + "="*60)
    print("🔍 PARSING SPECIFICATION")
    print("="*60)
    
    # Extract manufacturers
    manufacturers = []
    mfr_patterns = [
        r'(?i)manufacturer[s]?:\s*([^\n]+)',
        r'(?i)(?:Carlisle|GAF|Firestone|Johns Manville|Versico|Siplast|SOPREMA|Sika|Barrett|Tremco)',
    ]
    
    for pattern in mfr_patterns:
        matches = re.findall(pattern, text)
        manufacturers.extend(matches)
    
    manufacturers = deduplicate_list(manufacturers)
    print(f"  ✓ Found {len(manufacturers)} manufacturers")
    
    # Extract products
    products = []
    product_patterns = [
        r'(?i)product[s]?:\s*([^\n]+)',
        r'(?i)[A-Z][a-z]+\s+\d+\s*mil',
    ]
    
    for pattern in product_patterns:
        matches = re.findall(pattern, text)
        products.extend(matches)
    
    products = deduplicate_list(products)
    print(f"  ✓ Found {len(products)} products")
    
    result = {
        'manufacturers': manufacturers[:10] if manufacturers else None,
        'products': products[:15] if products else None
    }
    
    print("="*60 + "\n")
    return result

def parse_drawing_file(text, filename):
    """Parse a single architectural drawing file"""
    print("\n" + "="*60)
    print(f"🏗️  PARSING ARCHITECTURAL DRAWING: {filename}")
    print("="*60)
    
    try:
        # Use the enhanced parser
        parsed = parse_architectural_drawing(text)
        
        # Add filename to result
        parsed['filename'] = filename
        
        # Print summary
        if 'roof_plans' in parsed and parsed['roof_plans']:
            print(f"\n  📊 EXTRACTION SUMMARY:")
            for i, plan in enumerate(parsed['roof_plans'], 1):
                print(f"\n  Roof Plan {i}:")
                print(f"    Sheet: {plan.get('detail_number', 'Unknown')}")
                print(f"    Type: {plan.get('type', 'Unknown')}")
                print(f"    Drains: {plan.get('drains', 'N/A')}")
                print(f"    Scuppers: {plan.get('scuppers', 'N/A')}")
                print(f"    RTUs/Curbs: {plan.get('rtus_curbs', 'N/A')}")
                print(f"    Penetrations: {plan.get('penetrations', 'N/A')}")
                print(f"    Square Footage: {plan.get('square_footage', 'N/A')}")
                print(f"    Scale: {plan.get('scale', 'N/A')}")
                
                if plan.get('legend_items'):
                    print(f"    Legend Items: {len(plan['legend_items'])} found")
        else:
            print("  ⚠️  No roof plans detected in document")
        
        print("\n" + "="*60 + "\n")
        return parsed
        
    except Exception as e:
        print(f"  ❌ ERROR parsing drawing: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return {
            'error': str(e),
            'filename': filename,
            'drawing_type': 'Error',
            'roof_plans': []
        }

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse_files():
    """Main parsing endpoint - handles all document types"""
    print("\n" + "🚀 " + "="*58)
    print("🚀  NEW PARSING REQUEST RECEIVED")
    print("🚀 " + "="*58 + "\n")
    
    results = {
        'scope': None,
        'spec': None,
        'drawing': None,
        'assembly': None
    }
    
    # Process each category
    for category in ['scope', 'spec', 'drawing', 'assembly']:
        if category not in request.files:
            continue
        
        files = request.files.getlist(category)
        if not files or not files[0].filename:
            continue
        
        print(f"\n📂 Processing {len(files)} file(s) for category: {category.upper()}")
        print("-" * 60)
        
        # Handle multiple files for drawings, assemblies, and specs
        if category in ['drawing', 'assembly', 'spec'] and len(files) > 1:
            results[category] = []

            for file in files:
                if file and file.filename:
                    # Save file
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filepath)
                    print(f"\n  📥 Saved: {file.filename}")

                    # Parse based on category
                    if category == 'drawing':
                        text = extract_text_from_pdf(filepath)
                        if not text or len(text.strip()) < 50:
                            print(f"  ⚠️  Warning: Very little text extracted ({len(text)} chars)")
                        parsed = parse_drawing_file(text, file.filename)
                        results[category].append(parsed)

                    elif category == 'assembly':
                        text = extract_text_from_pdf(filepath)
                        if not text or len(text.strip()) < 50:
                            print(f"  ⚠️  Warning: Very little text extracted ({len(text)} chars)")
                        parsed = parse_assembly_letter(text)
                        parsed['filename'] = file.filename
                        results[category].append(parsed)

                    elif category == 'spec':
                        parser = SpecParser(filepath)
                        parsed = parser.parse()
                        parsed['filename'] = file.filename
                        results[category].append(parsed)
        
        # Handle single file
        else:
            file = files[0]
            if file and file.filename:
                # Save file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                print(f"\n  📥 Saved: {file.filename}")

                # Parse based on category
                if category == 'scope':
                    results['scope'] = parse_scope(filepath)

                elif category == 'spec':
                    parser = SpecParser(filepath)
                    parsed = parser.parse()
                    parsed['filename'] = file.filename
                    results['spec'] = [parsed]  # Return as list for consistency with multiple files

                elif category == 'drawing':
                    text = extract_text_from_pdf(filepath)
                    if not text or len(text.strip()) < 50:
                        print(f"  ⚠️  Warning: Very little text extracted ({len(text)} chars)")
                    results['drawing'] = parse_drawing_file(text, file.filename)

                elif category == 'assembly':
                    text = extract_text_from_pdf(filepath)
                    if not text or len(text.strip()) < 50:
                        print(f"  ⚠️  Warning: Very little text extracted ({len(text)} chars)")
                    parsed = parse_assembly_letter(text)
                    parsed['filename'] = file.filename
                    results['assembly'] = parsed
    
    print("\n" + "✅ " + "="*58)
    print("✅  PARSING COMPLETE - SENDING RESULTS")
    print("✅ " + "="*58 + "\n")
    
    # Debug: Print result structure
    print("📤 RESULTS STRUCTURE:")
    for key, value in results.items():
        if value:
            if isinstance(value, list):
                print(f"  {key}: [{len(value)} items]")
            elif isinstance(value, dict):
                print(f"  {key}: {{...}}")
            else:
                print(f"  {key}: {type(value)}")
        else:
            print(f"  {key}: None")
    print()
    
    # Convert to JSON-safe format and return
    safe_results = safe_jsonify(results)
    return jsonify(safe_results)

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "🏗️ " + "="*58)
    print("🏗️  ASSEMBLY DRAWING ARCHIVE TOOL - V2")
    print("🏗️  Flask server starting...")
    print("🏗️ " + "="*58 + "\n")
    # Use PORT from environment (Railway sets this) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # host='0.0.0.0' makes it accessible on your network
    # Remove debug=True for production
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', debug=debug_mode, port=port)