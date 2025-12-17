"""
Test script to verify pdfplumber integration across all parsers.
"""
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_pdf_extractor():
    """Test the pdf_extractor module"""
    print("\n" + "="*70)
    print("TESTING: pdf_extractor.py")
    print("="*70)

    try:
        from parsers.pdf_extractor import extract_text_from_pdf

        # Find a sample PDF in uploads
        upload_dir = Path(__file__).parent / 'static' / 'uploads'
        pdf_files = list(upload_dir.glob('*.pdf'))

        if not pdf_files:
            print("⚠️  No PDF files found in static/uploads/")
            return False

        test_file = pdf_files[0]
        print(f"📄 Testing with: {test_file.name}")

        text = extract_text_from_pdf(str(test_file))

        if text:
            print(f"✅ SUCCESS: Extracted {len(text)} characters")
            print(f"   Preview: {text[:200]}...")
            return True
        else:
            print("❌ FAILED: No text extracted")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_text_cleaner():
    """Test the text_cleaner module"""
    print("\n" + "="*70)
    print("TESTING: text_cleaner.py")
    print("="*70)

    try:
        from parsers.text_cleaner import extract_text_from_file

        # Find a sample PDF
        upload_dir = Path(__file__).parent / 'static' / 'uploads'
        pdf_files = list(upload_dir.glob('*.pdf'))

        if not pdf_files:
            print("⚠️  No PDF files found in static/uploads/")
            return False

        test_file = pdf_files[0]
        print(f"📄 Testing with: {test_file.name}")

        text = extract_text_from_file(str(test_file))

        if text:
            print(f"✅ SUCCESS: Extracted {len(text)} characters")
            print(f"   Preview: {text[:200]}...")
            return True
        else:
            print("❌ FAILED: No text extracted")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scope_parser():
    """Test the scope_parser module"""
    print("\n" + "="*70)
    print("TESTING: scope_parser.py")
    print("="*70)

    try:
        from parsers.scope_parser import parse_scope

        # Find a sample PDF
        upload_dir = Path(__file__).parent / 'static' / 'uploads'
        pdf_files = [f for f in upload_dir.glob('*.pdf') if 'SOW' in f.name or 'Scope' in f.name]

        if not pdf_files:
            pdf_files = list(upload_dir.glob('*.pdf'))

        if not pdf_files:
            print("⚠️  No PDF files found in static/uploads/")
            return False

        test_file = pdf_files[0]
        print(f"📄 Testing with: {test_file.name}")

        result = parse_scope(str(test_file))

        if result:
            print(f"✅ SUCCESS: Parsed scope document")
            print(f"   Materials: {len(result.get('materials', []))}")
            print(f"   Requirements: {len(result.get('requirements', []))}")
            print(f"   Summary length: {len(result.get('summary', ''))}")
            return True
        else:
            print("❌ FAILED: No result returned")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_spec_parser():
    """Test the spec_parser module"""
    print("\n" + "="*70)
    print("TESTING: spec_parser.py")
    print("="*70)

    try:
        from parsers.spec_parser import SpecParser

        # Find a sample spec PDF
        upload_dir = Path(__file__).parent / 'static' / 'uploads'
        pdf_files = [f for f in upload_dir.glob('*.pdf') if any(x in f.name for x in ['Spec', 'spec', '07'])]

        if not pdf_files:
            pdf_files = list(upload_dir.glob('*.pdf'))

        if not pdf_files:
            print("⚠️  No PDF files found in static/uploads/")
            return False

        test_file = pdf_files[0]
        print(f"📄 Testing with: {test_file.name}")

        parser = SpecParser(str(test_file))
        result = parser.parse()

        if result and result.get('status') == 'success':
            print(f"✅ SUCCESS: Parsed specification")
            print(f"   Section: {result.get('spec_section', 'N/A')}")
            print(f"   Title: {result.get('spec_title', 'N/A')}")
            print(f"   Manufacturers: {len(result.get('manufacturers', []))}")
            print(f"   Products: {len(result.get('products', []))}")
            print(f"   Shop Drawing Reqs: {len(result.get('shop_drawing_requirements', []))}")
            return True
        else:
            print(f"⚠️  Result: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', 'N/A')}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("PDFPLUMBER INTEGRATION TEST SUITE")
    print("="*70)

    results = {
        'pdf_extractor': test_pdf_extractor(),
        'text_cleaner': test_text_cleaner(),
        'scope_parser': test_scope_parser(),
        'spec_parser': test_spec_parser()
    }

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {test_name}")

    total = len(results)
    passed = sum(results.values())

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! pdfplumber integration successful!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
