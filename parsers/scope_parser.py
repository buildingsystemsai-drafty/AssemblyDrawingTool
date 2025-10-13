"""
Parser for scope of work documents.
Extracts materials, requirements, and project scope details.
"""
from .text_cleaner import (
    extract_text_from_file,
    extract_items,
    extract_r_values,
    extract_summary,
    deduplicate_list
)


def parse_scope(path):
    """
    Parse scope of work documents.
    Returns materials, requirements, and summary.
    """
    # Extract and clean text
    text = extract_text_from_file(path)
    
    if not text:
        return {
            'materials': [],
            'requirements': [],
            'summary': ''
        }
    
    # Extract materials
    material_patterns = [
        r'(membrane[^.]{0,80})',
        r'(insulation[^.]{0,80})',
        r'(fastener[^.]{0,80})',
        r'(roofing assembly[^.]{0,80})',
        r'(tapered[^.]{0,80})',
        r'(coverboard[^.]{0,80})',
        r'(vapor barrier[^.]{0,80})',
        r'(thermal barrier[^.]{0,80})'
    ]
    materials = extract_items(text, material_patterns, max_length=120)
    
    # Extract R-values and add to materials
    r_values = extract_r_values(text)
    materials.extend(r_values)
    
    # Deduplicate
    materials = deduplicate_list(materials)
    
    # Extract requirements
    requirement_patterns = [
        r'(shop drawing requirements[^.]{0,100})',
        r'(provide shop drawings[^.]{0,100})',
        r'(submit[^.]{0,80})',
        r'(approval required[^.]{0,80})',
        r'(coordinate with[^.]{0,80})'
    ]
    requirements = extract_items(text, requirement_patterns, max_length=120)
    requirements = deduplicate_list(requirements)
    
    # Extract clean summary
    summary = extract_summary(text, max_length=400)
    
    return {
        'materials': materials[:15],  # Top 15 materials
        'requirements': requirements[:8],  # Top 8 requirements
        'summary': summary
    }