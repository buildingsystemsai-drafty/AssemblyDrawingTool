"""
Test script for DXF generator
"""
from parsers.pdf_extractor import extract_text_from_pdf
from parsers.assembly_parser import parse_assembly_letter
from generators.dxf_generator import generate_assembly_dxf
import os

def test_with_your_carlisle_letter():
    """Test with the Carlisle MSU Harper Tubman letter"""
    
    print("🔧 Testing DXF Generator")
    print("=" * 50)
    
    # Path to your assembly letter PDF
    pdf_path = input("Enter path to your assembly letter PDF: ").strip().strip('"')
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found at {pdf_path}")
        return
    
    print(f"\n📄 Reading PDF: {os.path.basename(pdf_path)}")
    
    # Step 1: Extract text
    print("\n1️⃣ Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    print(f"   ✅ Extracted {len(text)} characters")
    
    # Step 2: Parse assembly
    print("\n2️⃣ Parsing assembly letter...")
    parsed_data = parse_assembly_letter(text)
    
    # Show what was parsed
    if 'assemblies' in parsed_data:
        print(f"   ✅ Found {len(parsed_data['assemblies'])} assemblies:")
        for i, assembly in enumerate(parsed_data['assemblies'], 1):
            print(f"      • {assembly.get('assembly_roof_area', f'Assembly {i}')}")
    else:
        print(f"   ✅ Parsed single assembly")
    
    print(f"\n   📋 Components found:")
    # Count components in first assembly
    first_assembly = parsed_data['assemblies'][0] if 'assemblies' in parsed_data else parsed_data
    
    if 'membrane_1' in first_assembly:
        print(f"      ✓ Membrane: {first_assembly['membrane_1'][:50]}...")
    if 'coverboard_1' in first_assembly:
        print(f"      ✓ Coverboard: {first_assembly['coverboard_1'][:50]}...")
    
    insul_count = sum(1 for key in first_assembly if key.startswith('insulation_layer_'))
    if insul_count > 0:
        print(f"      ✓ Insulation layers: {insul_count}")
    
    if 'vapor_barrier' in first_assembly:
        print(f"      ✓ Vapor barrier: Yes")
    
    if 'deck_slope' in first_assembly:
        print(f"      ✓ Deck: {first_assembly['deck_slope'][:50]}...")
    
    # Step 3: Generate DXF
    print("\n3️⃣ Generating DXF files...")
    try:
        # Create output folder if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        output_files = generate_assembly_dxf(parsed_data)
        
        print(f"   ✅ Generated {len(output_files)} DXF file(s):")
        for filename in output_files:
            filepath = os.path.join('output', filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"      📐 {filename} ({size:,} bytes)")
            else:
                print(f"      📐 {filename} (file not found)")
        
        print(f"\n✨ Success! Files saved in 'output' folder")
        print(f"\n📍 Next steps:")
        print(f"   1. Open AutoCAD or BricsCAD")
        print(f"   2. File → Open → Navigate to output folder")
        print(f"   3. Open any of the generated DXF files")
        
        return output_files
        
    except Exception as e:
        print(f"\n❌ Error generating DXF: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def test_with_sample_data():
    """Test with hardcoded sample data (no PDF needed)"""
    
    print("🔧 Testing with Sample Data")
    print("=" * 50)
    
    # Create sample parsed data matching your parser format
    sample_data = {
        'manufacturer': 'Carlisle',
        'project_name': 'Test Project',
        'project_location': 'Baltimore, MD',
        'assemblies': [{
            'assembly_roof_area': 'Test Assembly',
            'membrane_1': '60-mil Sure-Weld TPO membrane',
            'membrane_1_attachment': 'adhered with Sure-Weld Low-VOC Bonding Adhesive',
            'coverboard_1': 'DensDeck Prime: 1/2"',
            'coverboard_1_attachment': 'adhered with Flexible FAST Adhesive',
            'insulation_layer_1': '2.6" thick InsulBase Polyisocyanurate insulation',
            'insulation_layer_1_attachment': 'adhered with Flexible FAST Adhesive',
            'insulation_layer_2': '2.6" thick + Tapered InsulBase Polyisocyanurate insulation',
            'insulation_layer_2_attachment': 'adhered with Flexible FAST Adhesive',
            'deck_slope': 'Existing Gypsum deck',
        }]
    }
    
    print("\n1️⃣ Using sample data...")
    print("   ✅ Sample assembly created")
    
    print("\n2️⃣ Generating DXF...")
    try:
        # Create output folder if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        output_files = generate_assembly_dxf(sample_data)
        
        print(f"   ✅ Generated {len(output_files)} file(s):")
        for filename in output_files:
            filepath = os.path.join('output', filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"      📐 {filename} ({size:,} bytes)")
            else:
                print(f"      📐 {filename} (file not found)")
        
        print(f"\n✨ Success! Check the 'output' folder")
        print(f"\n📂 Location: {os.path.abspath('output')}")
        return output_files
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🏗️  Assembly DXF Generator - Test Suite")
    print("="*50)
    
    print("\nChoose test mode:")
    print("1. Test with your assembly letter PDF")
    print("2. Test with sample data (no PDF needed)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_with_your_carlisle_letter()
    elif choice == "2":
        test_with_sample_data()
    else:
        print("Invalid choice")