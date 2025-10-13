"""
Parser for architectural drawings.
Extracts detail callouts, sheet references, and drawing notes.
"""
from .text_cleaner import (
    extract_text_from_file,
    extract_items,
    deduplicate_list
)


def parse_drawings(path):
    """
    Parse architectural drawing PDFs.
    Returns callouts, sheet references, and notes.
    """
    # Extract and clean text
    text = extract_text_from_file(path)
    
    if not text:
        return {
            'callouts': [],
            'sheets': []
        }
    
    # Extract detail callouts
    callout_patterns = [
        r'(detail\s+\d+[A-Za-z]?[^.]{0,40})',
        r'(section\s+\d+\.?\d*[^.]{0,40})',
        r'(typ\.?[^.]{0,30})',
        r'(see detail[^.]{0,40})',
        r'(ref\. dwg[^.]{0,40})'
    ]
    callouts = extract_items(text, callout_patterns, max_length=80)
    callouts = deduplicate_list(callouts)
    
    # Extract sheet references
    sheet_patterns = [
        r'(sheet\s+[A-Za-z0-9\-\.]+)',
        r'(drawing\s+[A-Za-z0-9\-\.]+)',
        r'(index of drawings[^.]{0,60})',
        r'(sheet index[^.]{0,60})'
    ]
    sheets = extract_items(text, sheet_patterns, max_length=60)
    sheets = deduplicate_list(sheets)
    
    return {
        'callouts': callouts[:12],  # Top 12 callouts
        'sheets': sheets[:10]  # Top 10 sheets
    }