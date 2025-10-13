"""
Enhanced Architectural Drawing Parser
Multi-layered detection with confidence scoring for roof plans
"""
import re
from collections import defaultdict

# ============================================================================
# MAIN PARSING FUNCTION
# ============================================================================

def parse_architectural_drawing(text):
    """
    Enhanced parser with multi-layered detection for architectural roof drawings.
    Uses multiple detection strategies with confidence scoring.
    """
    result = {
        'drawing_type': 'Architectural Drawing',
        'roof_plans': []
    }
    
    # Extract all roof plan sections
    roof_sections = extract_roof_sections(text)
    
    for section in roof_sections:
        # Get raw detection data
        drains_data = count_drains(section['text'])
        scuppers_data = count_scuppers(section['text'])
        rtus_data = count_rtus(section['text'])
        pens_data = count_penetrations(section['text'])
        sf_data = extract_square_footage(section['text'])
        scale_data = extract_scale(section['text'])
        legend_data = extract_legend(section['text'])
        
        roof_plan = {
            'detail_number': section.get('detail_number', 'Unknown'),
            'type': section.get('type', 'ROOF PLAN'),
            'drains': format_for_display(drains_data, 'drains'),
            'scuppers': format_for_display(scuppers_data, 'scuppers'),
            'rtus_curbs': format_for_display(rtus_data, 'RTUs/Curbs'),
            'penetrations': format_for_display(pens_data, 'penetrations'),
            'square_footage': format_sf_for_display(sf_data),
            'scale': format_scale_for_display(scale_data),
            'legend_items': legend_data,
            # Keep raw data for debugging
            '_raw_data': {
                'drains': drains_data,
                'scuppers': scuppers_data,
                'rtus': rtus_data,
                'penetrations': pens_data
            }
        }
        result['roof_plans'].append(roof_plan)
    
    return result

# ============================================================================
# SECTION EXTRACTION
# ============================================================================

def extract_roof_sections(text):
    """Extract individual roof plan sections from the document."""
    sections = []
    
    # Split text into manageable chunks (simulate page/section breaks)
    lines = text.split('\n')
    current_section = {'text': '', 'detail_number': None, 'type': None}
    
    for i, line in enumerate(lines):
        # Look for sheet/detail identifiers
        detail_match = re.search(r'\b([A-Z]-?\d+(?:\.\d+)?)\b', line)
        type_match = re.search(r'\b(ROOF\s+PLAN|ROOF\s+DETAIL|ROOF\s+FRAMING)\b', line, re.IGNORECASE)
        
        if detail_match and not current_section['detail_number']:
            current_section['detail_number'] = detail_match.group(1)
        
        if type_match:
            current_section['type'] = type_match.group(1).upper()
        
        current_section['text'] += line + '\n'
        
        # Start new section on certain markers
        if i > 0 and (type_match or (i % 100 == 0 and current_section['text'])):
            if current_section['text'].strip():
                sections.append(current_section)
            current_section = {'text': '', 'detail_number': None, 'type': None}
    
    # Add the last section
    if current_section['text'].strip():
        sections.append(current_section)
    
    # If no sections found, treat entire text as one section
    if not sections:
        sections = [{'text': text, 'detail_number': 'A4', 'type': 'ROOF PLAN'}]
    
    return sections

# ============================================================================
# MULTI-LAYERED DETECTION FUNCTIONS
# ============================================================================

def count_drains(text):
    """Multi-layered detection for roof drains."""
    detections = []
    
    # Layer 1: Explicit numbered references (HIGHEST CONFIDENCE)
    explicit_patterns = [
        r'\((\d+)\)\s*(?:ROOF\s*)?DRAINS?',
        r'(\d+)\s*DRAINS?\s*TOTAL',
        r'DRAINS?\s*\((\d+)\)',
    ]
    
    for pattern in explicit_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            count = max(int(m) for m in matches)
            detections.append({
                'count': count,
                'method': 'explicit',
                'confidence': 0.95,
                'source': f'Found explicit count: ({count}) DRAINS'
            })
    
    # Layer 2: Standard abbreviations (HIGH CONFIDENCE)
    abbrev_patterns = [
        r'\bRD\b',
        r'\bR\.D\.\b',
        r'ROOF\s+DRAIN',
    ]
    
    abbrev_count = 0
    for pattern in abbrev_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        abbrev_count += len(matches)
    
    if abbrev_count > 0:
        detections.append({
            'count': abbrev_count,
            'method': 'abbreviation',
            'confidence': 0.80,
            'source': f'Found {abbrev_count} RD abbreviations'
        })
    
    # Layer 3: Legend table extraction (MEDIUM-HIGH CONFIDENCE)
    legend_drain_count = count_from_legend(text, ['drain', 'rd'])
    if legend_drain_count > 0:
        detections.append({
            'count': legend_drain_count,
            'method': 'legend',
            'confidence': 0.75,
            'source': f'Found {legend_drain_count} drain symbols in legend'
        })
    
    # Layer 4: Contextual mention counting (LOW CONFIDENCE - FALLBACK)
    mention_count = len(re.findall(r'\bdrain\b', text, re.IGNORECASE))
    
    if mention_count > 0 and not detections:
        detections.append({
            'count': mention_count,
            'method': 'mentions_fallback',
            'confidence': 0.40,
            'source': f'({mention_count}) drains mentioned (fallback count)'
        })
    
    # Return the highest confidence detection
    if detections:
        return max(detections, key=lambda x: x['confidence'])
    
    return {
        'count': 0,
        'method': 'none',
        'confidence': 0.0,
        'source': 'No drains detected'
    }

def count_scuppers(text):
    """Multi-layered detection for scuppers."""
    detections = []
    
    # Layer 1: Explicit numbered references
    explicit_patterns = [
        r'\((\d+)\)\s*SCUPPERS?',
        r'(\d+)\s*SCUPPERS?\s*TOTAL',
        r'SCUPPERS?\s*\((\d+)\)',
    ]
    
    for pattern in explicit_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            count = max(int(m) for m in matches)
            detections.append({
                'count': count,
                'method': 'explicit',
                'confidence': 0.95,
                'source': f'Found explicit count: ({count}) SCUPPERS'
            })
    
    # Layer 2: Abbreviations
    abbrev_patterns = [
        r'\bSC\b',
        r'\bS\.C\.\b',
    ]
    
    abbrev_count = 0
    for pattern in abbrev_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        abbrev_count += len(matches)
    
    if abbrev_count > 0:
        detections.append({
            'count': abbrev_count,
            'method': 'abbreviation',
            'confidence': 0.80,
            'source': f'Found {abbrev_count} SC abbreviations'
        })
    
    # Layer 3: Legend extraction
    legend_count = count_from_legend(text, ['scupper', 'sc'])
    if legend_count > 0:
        detections.append({
            'count': legend_count,
            'method': 'legend',
            'confidence': 0.75,
            'source': f'Found {legend_count} scupper symbols in legend'
        })
    
    # Layer 4: Type detection (overflow vs primary)
    scupper_type = detect_scupper_type(text)
    
    # Layer 5: Mention counting (fallback)
    mention_count = len(re.findall(r'\bscupper\b', text, re.IGNORECASE))
    
    if mention_count > 0 and not detections:
        detections.append({
            'count': mention_count,
            'method': 'mentions_fallback',
            'confidence': 0.40,
            'source': f'({mention_count}) scuppers mentioned (fallback count)'
        })
    
    # Return best detection with type info
    if detections:
        best = max(detections, key=lambda x: x['confidence'])
        if scupper_type:
            best['type'] = scupper_type
        return best
    
    return {
        'count': 0,
        'method': 'none',
        'confidence': 0.0,
        'source': 'No scuppers detected'
    }

def count_rtus(text):
    """Multi-layered detection for RTUs (Roof Top Units) and curbs."""
    detections = []
    
    # Layer 1: Explicit counts
    explicit_patterns = [
        r'\((\d+)\)\s*RTU[Ss]?',
        r'(\d+)\s*RTU[Ss]?\s*TOTAL',
        r'RTU[Ss]?\s*\((\d+)\)',
        r'\((\d+)\)\s*ROOF\s+TOP\s+UNITS?',
    ]
    
    for pattern in explicit_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            count = max(int(m) for m in matches)
            detections.append({
                'count': count,
                'method': 'explicit',
                'confidence': 0.95,
                'source': f'Found explicit count: ({count}) RTUs'
            })
    
    # Layer 2: Abbreviations
    rtu_count = len(re.findall(r'\bRTU\b', text, re.IGNORECASE))
    curb_count = len(re.findall(r'\bCURB\b', text, re.IGNORECASE))
    
    if rtu_count > 0:
        detections.append({
            'count': rtu_count,
            'method': 'abbreviation',
            'confidence': 0.80,
            'source': f'Found {rtu_count} RTU mentions',
            'curbs': curb_count
        })
    
    # Layer 3: Contextual mentions (fallback)
    mention_patterns = [
        r'roof\s+top\s+unit',
        r'rooftop\s+unit',
    ]
    
    mention_count = 0
    for pattern in mention_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        mention_count += len(matches)
    
    if mention_count > 0 and not detections:
        detections.append({
            'count': mention_count,
            'method': 'mentions_fallback',
            'confidence': 0.40,
            'source': f'({mention_count}) RTUs/Curbs mentioned (fallback count)'
        })
    
    if detections:
        return max(detections, key=lambda x: x['confidence'])
    
    return {
        'count': 0,
        'method': 'none',
        'confidence': 0.0,
        'source': 'No RTUs detected'
    }

def count_penetrations(text):
    """Multi-layered detection for roof penetrations."""
    detections = []
    
    # Layer 1: Explicit counts
    explicit_patterns = [
        r'\((\d+)\)\s*PENETRATIONS?',
        r'(\d+)\s*PENETRATIONS?\s*TOTAL',
        r'PENETRATIONS?\s*\((\d+)\)',
        r'\((\d+)\)\s*PIPE\s+PENETRATIONS?',
    ]
    
    for pattern in explicit_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            count = max(int(m) for m in matches)
            detections.append({
                'count': count,
                'method': 'explicit',
                'confidence': 0.95,
                'source': f'Found explicit count: ({count}) PENETRATIONS'
            })
    
    # Layer 2: Abbreviations
    abbrev_patterns = [
        r'\bPP\b',
        r'\bP\.P\.\b',
        r'PIPE\s+PENETRATION',
    ]
    
    abbrev_count = 0
    for pattern in abbrev_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        abbrev_count += len(matches)
    
    if abbrev_count > 0:
        detections.append({
            'count': abbrev_count,
            'method': 'abbreviation',
            'confidence': 0.80,
            'source': f'Found {abbrev_count} PP abbreviations'
        })
    
    # Layer 3: Mention counting (fallback)
    mention_count = len(re.findall(r'\bpenetration\b', text, re.IGNORECASE))
    
    if mention_count > 0 and not detections:
        detections.append({
            'count': mention_count,
            'method': 'mentions_fallback',
            'confidence': 0.40,
            'source': f'({mention_count}) penetrations mentioned (fallback count)'
        })
    
    if detections:
        return max(detections, key=lambda x: x['confidence'])
    
    return {
        'count': 0,
        'method': 'none',
        'confidence': 0.0,
        'source': 'No penetrations detected'
    }

# ============================================================================
# HELPER DETECTION FUNCTIONS
# ============================================================================

def detect_scupper_type(text):
    """Detect if scuppers are primary or overflow."""
    overflow_indicators = [
        r'overflow\s+scupper',
        r'emergency\s+scupper',
        r'2"\s+above\s+roof',
        r'secondary\s+drainage',
    ]
    
    primary_indicators = [
        r'primary\s+scupper',
        r'flush\s+with\s+roof',
        r'main\s+drainage',
    ]
    
    for pattern in overflow_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return 'overflow'
    
    for pattern in primary_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return 'primary'
    
    return None

def count_from_legend(text, keywords):
    """Extract counts from legend/symbol tables."""
    legend_section = extract_legend_section(text)
    if not legend_section:
        return 0
    
    count = 0
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        matches = re.findall(pattern, legend_section, re.IGNORECASE)
        count += len(matches)
    
    return count

def extract_legend_section(text):
    """Extract the legend/symbols section from the drawing."""
    legend_patterns = [
        r'LEGEND[\s\S]{0,500}',
        r'SYMBOLS[\s\S]{0,500}',
        r'KEY[\s\S]{0,500}',
    ]
    
    for pattern in legend_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def extract_legend(text):
    """Extract legend items as key-value pairs."""
    legend = {}
    legend_section = extract_legend_section(text)
    
    if not legend_section:
        return legend
    
    # Pattern 1: ABBREV = DESCRIPTION
    pattern1 = r'\b([A-Z]{2,4})\b\s*[=:–-]\s*([A-Z\s]+)'
    matches = re.findall(pattern1, legend_section)
    for abbrev, desc in matches:
        legend[abbrev.strip()] = desc.strip()
    
    # Pattern 2: Symbol = Description
    pattern2 = r'([○⊕△□▲●◇◆]+)\s*[=:]\s*([A-Z\s]+)'
    matches = re.findall(pattern2, legend_section)
    for symbol, desc in matches:
        legend[symbol] = desc.strip()
    
    return legend

def extract_square_footage(text):
    """Extract square footage from the drawing."""
    patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*(?:SF|S\.F\.|SQ\.?\s*FT\.?)',
        r'(\d{1,3}(?:,\d{3})*)\s*SQUARE\s+FEET',
        r'AREA[\s:]*(\d{1,3}(?:,\d{3})*)\s*SF',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sf_str = match.group(1).replace(',', '')
            return {
                'value': int(sf_str),
                'unit': 'SF',
                'source': match.group(0)
            }
    
    return {
        'value': None,
        'unit': 'SF',
        'source': 'Not found'
    }

def extract_scale(text):
    """Extract drawing scale."""
    patterns = [
        r'(?:SCALE|Scale)[\s:]*1\s*:\s*(\d+)',
        r'(?:SCALE|Scale)[\s:]*1/(\d+)"\s*=\s*1[\'"]?-?0[\'"]?',
        r'1\s*:\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return {
                'ratio': f'1:{match.group(1)}',
                'source': match.group(0)
            }
    
    return {
        'ratio': None,
        'source': 'Not found'
    }

# ============================================================================
# DISPLAY FORMATTING
# ============================================================================

def format_for_display(detection, element_name):
    """Format detection result for UI display."""
    if detection['count'] == 0:
        return f"No {element_name} detected"
    
    # Confidence indicators
    if detection['confidence'] >= 0.90:
        indicator = "✓✓✓"
        detail = "high confidence"
    elif detection['confidence'] >= 0.70:
        indicator = "✓✓"
        detail = "confirmed"
    else:
        indicator = "✓"
        detail = "estimated"
    
    # Format based on method
    if detection['method'] == 'explicit':
        return f"{indicator} ({detection['count']}) {element_name}"
    elif detection['method'] in ['abbreviation', 'legend']:
        return f"{indicator} ({detection['count']}) {element_name} - {detail}"
    else:
        return f"{indicator} ({detection['count']}) {element_name} mentioned (fallback)"

def format_sf_for_display(sf_data):
    """Format square footage for display."""
    if sf_data['value']:
        return f"{sf_data['value']:,} SF"
    return "Not specified"

def format_scale_for_display(scale_data):
    """Format scale for display."""
    if scale_data['ratio']:
        return scale_data['ratio']
    return "Not specified"