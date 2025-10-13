"""
Parser for Section 07 specifications.
Extracts warranty information, system types, and technical requirements.
"""
from .text_cleaner import (
    extract_text_from_file,
    extract_items,
    deduplicate_list
)


def parse_spec(path):
    """
    Parse Section 07 specification documents.
    Returns warranties, systems, and technical requirements.
    """
    # Extract and clean text
    text = extract_text_from_file(path)
    
    if not text:
        return {
            'warranties': [],
            'systems': []
        }
    
    # Extract warranty information
    warranty_patterns = [
        r'(warranty[^.]{0,100})',
        r'(\d+[-\s]year[^.]{0,80})',
        r'(guarantee[^.]{0,80})',
        r'(warranted for[^.]{0,80})'
    ]
    warranties = extract_items(text, warranty_patterns, max_length=120)
    warranties = deduplicate_list(warranties)
    
    # Extract system types
    system_patterns = [
        r'(roofing system[^.]{0,80})',
        r'(system type[^.]{0,80})',
        r'(assembly[^.]{0,60})',
        r'(single-ply[^.]{0,60})',
        r'(BUR system[^.]{0,60})',
        r'(modified bitumen[^.]{0,60})'
    ]
    systems = extract_items(text, system_patterns, max_length=100)
    systems = deduplicate_list(systems)
    
    return {
        'warranties': warranties[:8],  # Top 8 warranties
        'systems': systems[:8]  # Top 8 systems
    }