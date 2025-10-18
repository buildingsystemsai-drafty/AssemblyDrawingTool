🏗️ Assembly Drawing Archive Tool
A Flask-based web application for parsing and extracting structured data from roofing shop drawings, including scope of work documents, specifications, architectural drawings, and assembly letters.

📋 Features
Multi-Document Parsing: Upload and parse multiple document types simultaneously
Assembly Letter Extraction: Comprehensive parsing of roof assembly details including:
Multiple assembly detection (Main Roof, Receiving Room, Canopy, etc.)
Layer-by-layer breakdown (membranes, insulation, coverboards, vapor barriers)
Attachment methods and specifications
FM RoofNav, UL, and ASTM approvals
Scope of Work Parser: Extracts materials, requirements, and project summaries
Specification Parser: Identifies manufacturers and product specifications
Drawing Parser: Extracts elements and callouts from architectural drawings
Drag & Drop Interface: Modern, intuitive UI with file management
Multi-Manufacturer Support: Works with Carlisle, Mule-Hide, GAF, Firestone, Johns Manville, Siplast, SOPREMA, Versico
🚀 Installation
Prerequisites
Python 3.7+
pip
Setup
Clone the repository:
bash
   git clone https://github.com/buildingsystemsai-drafty/AssemblyDrawingTool.git
   cd AssemblyDrawingTool
Create a virtual environment:
bash
   python -m venv .venv
Activate the virtual environment:
Windows:
bash
     .venv\Scripts\activate
Mac/Linux:
bash
     source .venv/bin/activate
Install dependencies:
bash
   pip install -r requirements.txt
💻 Usage
Start the Flask server:
bash
   python app.py
Open your browser: Navigate to http://127.0.0.1:5000
Upload documents:
Drag and drop or click to upload PDFs in each category
Remove files by clicking the ✕ button
Click "Parse Documents" to extract data
View results: Parsed data is displayed in an organized format with:
Project information
Contractor details
Assembly breakdowns
Layer specifications
Approval ratings
📁 Project Structure
AssemblyDrawingTool/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .gitignore                      # Git ignore rules
├── parsers/
│   ├── __init__.py
│   ├── assembly_parser.py          # Assembly letter parser
│   ├── scope_parser.py             # Scope of work parser
│   ├── spec_parser.py              # Specification parser
│   ├── arch_drawing_parser.py      # Drawing parser
│   ├── pdf_extractor.py            # PDF text extraction
│   └── text_cleaner.py             # Text cleaning utilities
├── static/
│   └── js/
│       └── app.js                  # Frontend JavaScript
├── templates/
│   └── index.html                  # Main UI template
└── uploads/                        # Temporary file storage (gitignored)
🛠️ Technologies Used
Backend: Flask (Python)
PDF Processing: PyPDF2
Frontend: Vanilla JavaScript, HTML5, CSS3
Styling: Custom CSS with gradient design
Text Processing: Regex pattern matching
📊 Supported Document Types
Assembly Letters
Extracts up to 5 assemblies per document
Parses 3 membrane layers, 3 insulation layers, 2 coverboards
Captures attachment methods and specifications
Identifies FM, UL, and ASTM approvals
Scope of Work
Materials and requirements
Project summaries
Budget items
Specifications
Manufacturer identification
Product listings
System specifications
Drawings
Element extraction
Callout identification
Drawing annotations
🔧 Configuration
The application uses the following default settings:

Upload folder: ./uploads/
Port: 5000
Debug mode: Enabled (disable in production)
📝 Output Format
Parsed data is returned in JSON format and displayed in the UI with:

Hierarchical organization
Field labels matching Excel template format
Indented sub-items (attachment methods)
Color-coded sections
🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

📄 License
This project is private and proprietary.

👤 Author
Armand Lefebvre
🌐 roofshopdrawings.com

🐛 Known Issues
Large PDF files may take longer to process
OCR is required for image-based PDFs
Some manufacturer formats may require pattern adjustments
🔮 Future Enhancements
 Excel export functionality
 Database storage for parsed results
 Batch processing for multiple projects
 Advanced OCR integration
 User authentication
 Project comparison tools
Made with ❤️ for the roofing industry
 
## Branch: functioning_dxf_generator

This branch (`functioning_dxf_generator`) contains updates that make `generators/dxf_generator.py` functioning for DXF output generation. If you're running from this branch, the DXF generator has been tested locally and should produce valid DXF files for simple assemblies. See `generators/dxf_generator.py` for usage and examples.

