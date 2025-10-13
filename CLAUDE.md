# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AssemblyDrawingTool is a Flask-based web application for parsing and extracting structured data from roofing shop drawings. It processes multiple document types (scope of work, specifications, architectural drawings, assembly letters) and extracts critical information for the roofing industry.

## Development Commands

### Running the Application
```bash
python app.py
```
Note: `app.py` is currently deleted on branch `arch-drawing-parser-paused` but exists in git history. Restore it before running:
```bash
git restore app.py
```

### Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Testing Parsers Directly
Individual parsers can be run standalone:
```bash
python parsers/spec_parser.py <path_to_pdf>
```

## Architecture

### Application Flow
1. **Frontend** (templates/index.html + static/js/app.js): Multi-file upload interface with drag-and-drop
2. **Flask Backend** (app.py): Handles file uploads, coordinates parsing, returns JSON
3. **Parser Modules** (parsers/): Specialized document processors
4. **Output**: Structured JSON matching Excel template format for roofing assemblies

### Key Components

#### Flask Application (app.py)
- Single endpoint `/parse` accepting POST with multipart form data
- Accepts 4 document types: `scope`, `spec`, `drawing`, `assembly`
- Saves uploaded files to `static/uploads/`
- Routes files to appropriate parsers
- Returns consolidated JSON response

#### Parser Architecture (parsers/)

**spec_parser.py** - Specification document parser
- Extracts Division 07 specification details
- Uses `pdfplumber` for more reliable text extraction
- Identifies: spec section numbers, manufacturers, products, shop drawing requirements
- Structured extraction from SUBMITTAL sections (especially "Shop Drawings" subsections)
- Can process single files or entire directories

**scope_parser.py** - Scope of work parser
- Extracts materials, requirements, and project summaries
- Pattern-based extraction using regex
- Identifies R-values, membrane types, insulation details
- Returns top 15 materials and top 8 requirements

**assembly_parser.py** - Assembly letter parser (deleted, in git history)
- Parses manufacturer assembly letters (Carlisle, GAF, Firestone, etc.)
- Detects multiple assemblies per document (Main Roof, Receiving Room, Canopy, etc.)
- Extracts layer-by-layer breakdowns:
  - Membranes (up to 3 layers)
  - Insulation (up to 3 layers)
  - Coverboards (up to 2)
  - Vapor barriers
  - Attachment methods for each component
- Extracts FM RoofNav, UL, and ASTM approval ratings
- Output format matches Excel template column structure

**arch_drawing_parser.py** - Architectural drawing parser (deleted, in git history)
- Extracts roof elements: drains, scuppers, RTUs, penetrations
- Parses sheet numbers and drawing details

**text_cleaner.py** - Text utilities
- RTF formatting removal
- PDF text extraction helpers
- Pattern-based extraction functions
- Deduplication and normalization

**pdf_extractor.py** - PDF text extraction
- Basic PyPDF2-based extraction
- Used as fallback when pdfplumber not available

### Frontend Architecture (static/js/app.js)

**State Management**
- `fileStorage`: Tracks uploaded files per category
- `currentData`: Stores parsed results
- `workflowStates`: Tracks review/approval status per sheet
- LocalStorage used for session persistence

**Key Features**
- Multi-file uploads per category (drawing and assembly support multiple files)
- View toggling: table vs cards
- Search/filter functionality
- CSV export
- Modal detail views for specifications
- Workflow badges (detected, reviewing, verified, approved)

**API Integration**
- Single `/parse` endpoint via fetch POST
- FormData with multiple files per type
- Async/await pattern with loading states

## Important Patterns

### Multi-Assembly Detection
Assembly parser detects multiple roof areas in a single document by:
1. Scanning for section markers (e.g., "Main Store Roof", "Canopy Roofs")
2. Checking context (newlines before, assembly fields after)
3. Splitting text into sections
4. Parsing each section independently

### Excel Template Matching
Assembly parser output uses OrderedDict to ensure fields match Excel template column order:
- assembly_roof_area
- spec_number
- manufacturer
- system (type)
- date
- [membrane/insulation/coverboard layers with attachment methods]
- FM/UL/ASTM approvals

### PDF Processing
Two-tier approach:
1. **pdfplumber** (spec_parser.py): More reliable, extracts layout/structure
2. **PyPDF2** (pdf_extractor.py, scope_parser.py): Faster, less accurate

When PDFs fail extraction, returns OCR-required error message.

## Git Branch Context

Current branch: `arch-drawing-parser-paused`

Deleted files (available in git history):
- app.py (main Flask application)
- parsers/assembly_parser.py
- parsers/arch_drawing_parser.py

Modified files:
- parsers/spec_parser.py (enhanced with pdfplumber, detailed logging)
- static/js/app.js (added spec viewer, modal details, CSV export)

## Testing Strategy

Upload test documents via web interface:
1. Navigate to http://127.0.0.1:5000
2. Upload PDFs in each category
3. Click "Parse Documents"
4. Results display in JSON format with statistics

Validate parsers individually:
```bash
python parsers/spec_parser.py static/uploads/test-spec.pdf
```

## Output Format

Parsers return JSON with this structure:
```json
{
  "scope": { "materials": [], "requirements": [], "summary": "" },
  "spec": [{ "filename": "", "section": "", "title": "", "manufacturers": [], "products": [], "shop_drawing_requirements": [] }],
  "drawing": [{ "sheet_number": "", "drains": 0, "scuppers": 0, "rtus": 0 }],
  "assembly": { "manufacturer": "", "assemblies": [{ "layers": [], "approvals": {} }] }
}
```

## Manufacturer Support

Assembly parser handles multiple roofing manufacturers:
- Carlisle
- GAF
- Firestone
- Johns Manville
- Mule-Hide
- Siplast
- SOPREMA
- Versico

Each has slightly different assembly letter formats. Parser uses flexible pattern matching to handle variations.
