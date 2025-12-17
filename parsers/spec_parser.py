import re
import pdfplumber
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpecParser:
    """Parse Division 07 specification documents for shop drawing requirements"""
    
    def __init__(self, pdf_path=None, pdf_data=None):
        self.pdf_path = pdf_path
        self.pdf_data = pdf_data
        self.full_text = ""
        self.spec_number = ""
        self.spec_title = ""
        self.section_category = ""
        self.manufacturers = []
        self.products = []
        self.shop_drawing_requirements = []
        self.other_submittal_requirements = {}
        
    def parse(self) -> Dict:
        """Main parsing function"""
        logger.info(f"📄 Parsing specification: {self.pdf_path}")
        
        # Extract all text from PDF
        self.full_text = self._extract_text()
        
        if not self.full_text or len(self.full_text) < 100:
            return {
                "status": "error",
                "message": "No text found - PDF may need OCR",
                "text_length": len(self.full_text)
            }
        
        logger.info(f"✅ Extracted {len(self.full_text)} characters")
        
        # Identify spec section
        self._identify_spec_section()
        
        # Extract manufacturers and products
        self._extract_manufacturers_and_products()
        
        # Find and extract shop drawing requirements
        self._extract_shop_drawing_requirements()
        
        # Return structured results
        return self._compile_results()
    
    def _extract_text(self) -> str:
        """Extract text from PDF using pdfplumber"""
        text = ""
        
        try:
            # Use file path if provided, otherwise use binary data
            if self.pdf_path:
                with pdfplumber.open(self.pdf_path) as pdf:
                    logger.info(f"📖 PDF has {len(pdf.pages)} pages")
                    
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            logger.info(f"  ✓ Page {i+1}/{len(pdf.pages)} - {len(page_text)} chars")
                        else:
                            logger.warning(f"  ⚠️ Page {i+1}/{len(pdf.pages)}: No text (may need OCR)")
            elif self.pdf_data:
                # Handle binary PDF data if path not available
                import io
                with pdfplumber.open(io.BytesIO(self.pdf_data)) as pdf:
                    logger.info(f"📖 PDF has {len(pdf.pages)} pages")
                    
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            logger.info(f"  ✓ Page {i+1}/{len(pdf.pages)} - {len(page_text)} chars")
                        else:
                            logger.warning(f"  ⚠️ Page {i+1}/{len(pdf.pages)}: No text (may need OCR)")
                        
        except Exception as e:
            logger.error(f"❌ Error reading PDF: {e}")
            return ""
        
        # Clean and normalize text
        text = self._clean_text(text)
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better parsing."""
        # Replace common problematic characters
        text = re.sub(r'[â€™â€"]', "'", text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Fix common formatting issues
        text = text.replace(' :', ':')
        return text.strip()
    
    def _identify_spec_section(self):
        """Identify the specification section number and title"""
        # Look for patterns like "07 50 00" or "Section 07500"
        div07_patterns = [
            r'(?:SECTION\s+)?(\d{2}\s*\d{2}\s*\d{2}(?:\.\d{2})?)',  # 07 41 13.16 or 074113.16
            r'(?:SECTION\s+)?(\d{2}\s*\d{2}\s*\d{2})',  # 07 41 13 or 074113
            r'(?:SECTION\s+)?(\d{2}\s*\d{2})',  # 07 41 or 0741
            r'(?:DIVISION\s+)?(07)',  # Division 07
        ]
        
        for pattern in div07_patterns:
            match = re.search(pattern, self.full_text[:2000])
            if match:
                self.spec_number = match.group(1).replace(' ', '')
                logger.info(f"📋 Found spec section: {self.spec_number}")
                break
        
        # Look for spec title (usually on first page)
        title_patterns = [
            r'(?:SECTION\s+\d{2}\s*\d{2}\s*\d{2}(?:\.\d{2})?\s*[-–]\s*)([A-Z][A-Z\s]+)',
            r'(?:\d{2}\s*\d{2}\s*\d{2}(?:\.\d{2})?\s*[-–]\s*)([A-Z][A-Z\s]+)',
            r'(?:PART\s+1\s+[-–]\s+GENERAL\s+)(.*?)(?:\n|$)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, self.full_text[:3000])
            if match:
                self.spec_title = match.group(1).strip()
                logger.info(f"📝 Spec title: {self.spec_title}")
                break
                
        # Determine section category based on spec number
        if re.search(r'07\s*[234]\d', self.spec_number):
            self.section_category = "Roofing"
        elif re.search(r'07\s*[56]\d', self.spec_number):
            self.section_category = "Waterproofing"
        elif re.search(r'07\s*[78]\d', self.spec_number):
            self.section_category = "Wall Panel/Flashing"
        elif re.search(r'07\s*[9]\d', self.spec_number):
            self.section_category = "Joint Sealants"
        else:
            self.section_category = "Other Div07"
            
        logger.info(f"🔍 Section category: {self.section_category}")
    
    def _extract_manufacturers_and_products(self):
        """Extract manufacturers and products from specification"""
        # Extract manufacturers
        self._extract_manufacturers()
        
        # Extract products
        self._extract_products()
        
        logger.info(f"👨‍🏭 Found {len(self.manufacturers)} manufacturers")
        logger.info(f"🛠️ Found {len(self.products)} products")
    
    def _extract_manufacturers(self):
        """Extract manufacturers from specification"""
        # Look for manufacturer sections
        patterns = [
            r'(?:Basis-of-Design Product|Available Manufacturers|Manufacturers):.*?(?=\d\.|[A-Z]\.|PART\s+[23]|$)',
            r'Available (?:Products|Manufacturers):.*?(?=\d\.|[A-Z]\.|PART\s+[23]|$)',
            r'Subject to compliance with requirements, (?:available )?manufacturers (?:offering|that may be considered)',
            r'(?:Acceptable|Approved) Manufacturers:',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE | re.DOTALL)
            if match:
                manufacturer_text = match.group(0)
                
                # Look for manufacturer names in the text
                mfr_patterns = [
                    r'(?:[a-z]\.|[0-9]+\.|•)\s+([A-Z][A-Za-z\s\.\,\&\-]+?)(?:\.|\n)',
                    r'([A-Z][A-Za-z\s\.\,\&]+?),? Inc\.?',
                    r'([A-Z][A-Za-z\s\.\,\&]+?),? LLC\.?',
                    r'([A-Z][A-Za-z\s\.\,\&]+?) Company',
                    r'([A-Z][A-Za-z0-9\s\.\,\&\-]+?)\.',
                ]
                
                for mfr_pattern in mfr_patterns:
                    mfr_matches = re.finditer(mfr_pattern, manufacturer_text)
                    for mfr_match in mfr_matches:
                        mfr_name = mfr_match.group(1).strip()
                        if mfr_name and len(mfr_name) > 3 and mfr_name not in self.manufacturers:
                            self.manufacturers.append(mfr_name)
    
    def _extract_products(self):
        """Extract product information from specification"""
        # Look for product names in Part 2 - Products
        product_section = None
        
        # Find Products section
        products_pattern = r'PART\s+2\s+[-–]\s+PRODUCTS(.*?)(?:PART\s+3|EXECUTION|$)'
        match = re.search(products_pattern, self.full_text, re.IGNORECASE | re.DOTALL)
        
        if match:
            product_section = match.group(1)
            
            # Extract product names
            product_patterns = [
                r'\d+\.\d+\s+([A-Z][A-Z0-9\s\-]+)',
                r'[A-Z]\.\s+([A-Z][A-Za-z0-9\s\-]+):'
            ]
            
            for pattern in product_patterns:
                product_matches = re.finditer(pattern, product_section)
                for product_match in product_matches:
                    product_name = product_match.group(1).strip()
                    if product_name and len(product_name) > 3 and product_name not in self.products:
                        self.products.append(product_name)
    
    def _extract_shop_drawing_requirements(self):
        """Extract shop drawing requirements from SUBMITTALS section"""
        logger.info("\n🔍 Searching for SUBMITTALS section...")
        
        # Find SUBMITTALS section
        submittals_section = self._find_submittals_section()
        
        if not submittals_section:
            logger.warning("⚠️ Could not find SUBMITTALS section")
            return
        
        logger.info(f"✅ Found SUBMITTALS section ({len(submittals_section)} chars)")
        
        # Find Shop Drawings subsection within SUBMITTALS
        shop_drawings_section = self._find_shop_drawings_section(submittals_section)
        
        if not shop_drawings_section:
            logger.warning("⚠️ Could not find Shop Drawings subsection")
            return
        
        logger.info(f"✅ Found Shop Drawings subsection ({len(shop_drawings_section)} chars)")
        
        # Extract individual requirements
        self.shop_drawing_requirements = self._parse_requirements(shop_drawings_section)
        
        # Extract other submittal types
        self._extract_other_submittals(submittals_section)
        
        logger.info(f"✅ Extracted {len(self.shop_drawing_requirements)} shop drawing requirements")
    
    def _find_submittals_section(self) -> Optional[str]:
        """Find the SUBMITTALS section in the spec"""
        # Try finding ACTION SUBMITTALS first
        action_patterns = [
            r'(?:1\.\d+\s+)?ACTION\s+SUBMITTALS.*?(?=1\.\d+\s+\w+|PART\s+[23]|$)',
            r'(?:PART\s+1\s+[-–]\s+)?ACTION\s+SUBMITTALS.*?(?=PART\s+[234]|QUALITY|DELIVERY|WARRANTY|PRODUCTS|EXECUTION|$)',
        ]
        
        for pattern in action_patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        
        # If ACTION SUBMITTALS not found, look for general SUBMITTALS
        patterns = [
            r'(?:PART\s+1\s+[-–]\s+)?SUBMITTALS?(.*?)(?:PART\s+[234]|QUALITY|DELIVERY|WARRANTY|PRODUCTS|EXECUTION)',
            r'(?:1\.0?\d?\s+)?SUBMITTALS?(.*?)(?:1\.0?\d?\s+[A-Z]|2\.0)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.full_text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0) if pattern.startswith('(?:PART') else match.group(1)
        
        return None
    
    def _find_shop_drawings_section(self, submittals_text: str) -> Optional[str]:
        """Find Shop Drawings subsection within SUBMITTALS"""
        patterns = [
            r'(?:[A-Z]\.\s+)?SHOP\s+DRAWINGS?[:\s]+(.*?)(?:[A-Z]\.\s+[A-Z]|$)',
            r'(?:\d+\.\d+\s+)?SHOP\s+DRAWINGS?[:\s]+(.*?)(?:\d+\.\d+|$)',
            r'(?:[A-Z]\.\s+)?Shop\s+Drawings:(?:.*?)(?=[A-Z]\.\s+[A-Z]|$)',
            r'(?:\d+\.\s+)?Shop\s+Drawings:(?:.*?)(?=\d+\.\s+|$)',
            r'Shop\s+Drawings:(?:.*?)(?=Product|Samples|Certificates|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, submittals_text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        
        return None
    
    def _parse_requirements(self, text: str) -> List[str]:
        """Parse individual requirements from text"""
        requirements = []
        
        # First, check if text starts with "Shop Drawings:" and extract content after it
        if "Shop Drawings:" in text[:30]:
            text = text.split("Shop Drawings:", 1)[1].strip()
        
        # Split by numbered/lettered items
        # Look for patterns like "1.", "a.", "A.", etc.
        items = re.split(r'\n\s*(?:[0-9]+\.|[a-z]\.|[A-Z]\.|\d+\)|\w\)|\-|\•)\s+', text)
        
        # Process each item
        for item in items:
            item = item.strip()
            if len(item) > 15:  # Ignore very short fragments
                # Clean up the text
                item = re.sub(r'\s+', ' ', item)  # Normalize whitespace
                item = re.sub(r'\.{2,}', '', item)  # Remove dot leaders
                # Add period if missing
                if not item.endswith('.') and not item.endswith(':'):
                    item += '.'
                requirements.append(item)
        
        return requirements
    
    def _extract_other_submittals(self, submittals_text: str):
        """Extract other submittal requirements like product data, samples, etc."""
        submittal_types = [
            "Product Data", "Samples", "Qualification Data", "Product Test Reports", 
            "Field Reports", "Warranties", "Closeout Submittals", "Maintenance Data"
        ]
        
        for submittal_type in submittal_types:
            pattern = r'(?:[A-Z]\.\s+)?' + re.escape(submittal_type) + r':(?:.*?)(?=[A-Z]\.\s+[A-Z]|$)'
            match = re.search(pattern, submittals_text, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(0)
                requirements = self._parse_requirements(text)
                if requirements:
                    self.other_submittal_requirements[submittal_type] = requirements
    
    def _compile_results(self) -> Dict:
        """Compile all extracted data into structured format"""
        return {
            "status": "success",
            "spec_section": self.spec_number,
            "spec_title": self.spec_title,
            "section_category": self.section_category,
            "manufacturers": self.manufacturers,
            "products": self.products,
            "shop_drawing_requirements": self.shop_drawing_requirements,
            "other_submittal_requirements": self.other_submittal_requirements,
            "text_length": len(self.full_text)
        }


def main():
    """Example usage"""
    import sys
    import json
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python spec_parser.py <path_to_pdf>")
        print("\nExample: python spec_parser.py specs/07-50-00-membrane-roofing.pdf")
        return
    
    pdf_path = sys.argv[1]
    
    # Process directory of PDFs
    if os.path.isdir(pdf_path):
        results = []
        pdf_files = [f for f in os.listdir(pdf_path) if f.lower().endswith('.pdf')]
        
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_path, pdf_file)
            parser = SpecParser(file_path)
            result = parser.parse()
            results.append({"file": pdf_file, "results": result})
        
        # Save all results to JSON
        output_path = os.path.join(pdf_path, "spec_parsing_results.json")
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_path}")
    else:
        # Create parser and parse the spec
        parser = SpecParser(pdf_path)
        results = parser.parse()
        
        # Print shop drawing requirements
        if results["status"] == "success" and results["shop_drawing_requirements"]:
            print("\n" + "="*70)
            print(f"📋 SHOP DRAWING REQUIREMENTS: {results['spec_section']} - {results['spec_title']}")
            print("="*70)
            
            for i, req in enumerate(results["shop_drawing_requirements"], 1):
                print(f"{i}. {req}")
                
            print("="*70)
        else:
            print("\n⚠️ No shop drawing requirements found")
        
        # Optionally save to JSON
        if results["status"] == "success":
            output_path = pdf_path.replace('.pdf', '_parsed.json')
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {output_path}")


if __name__ == "__main__":
    main()