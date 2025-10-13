import re
from collections import OrderedDict
from parsers.text_cleaner import clean_rtf_text

def parse_assembly_letter(text):
    """
    Parse assembly letter matching Excel template format.
    Extracts each component and attachment method separately.
    """
    text = clean_rtf_text(text)
    
    manufacturer = extract_manufacturer(text)
    project_info = extract_project_info(text)
    
    # Detect assemblies
    assemblies = detect_multiple_assemblies(text)
    
    if len(assemblies) > 1:
        # Multiple assemblies
        result = OrderedDict()
        result['manufacturer'] = manufacturer
        
        if project_info:
            for key, value in project_info.items():
                result[f'project_{key}'] = value
        
        result['assemblies'] = []
        for assembly_name, assembly_text in assemblies:
            assembly_data = parse_single_assembly_excel_format(assembly_text, assembly_name, manufacturer, project_info)
            result['assemblies'].append(assembly_data)
        
        return result
    else:
        # Single assembly
        result = parse_single_assembly_excel_format(text, None, manufacturer, project_info)
        return result

def detect_multiple_assemblies(text):
    """Detect multiple assemblies."""
    section_markers = []
    
    patterns = [
        (r'(?i)(Main\s+Store\s+Roof)', 'Main Store Roof'),
        (r'(?i)(Receiving\s+Room\s+Roof)', 'Receiving Room Roof'),
        (r'(?i)(Canopy\s+Roofs?)', 'Canopy Roofs'),
        (r'(?i)(Office\s+Roof)', 'Office Roof'),
        (r'(?i)(Penthouse\s+Roof)', 'Penthouse Roof'),
        (r'(?i)(Loading\s+Dock\s+Roof)', 'Loading Dock Roof'),
        (r'(?i)(Roof\s+[A-Z]\b)', 'Roof'),
        (r'(?i)(Area\s+\d+)', 'Area'),
    ]
    
    for pattern, name_type in patterns:
        for match in re.finditer(pattern, text):
            pos = match.start()
            before_text = text[max(0, pos-50):pos]
            after_text = text[pos:min(len(text), pos+100)]
            
            has_newline_before = '\n' in before_text[-10:] or pos < 50
            has_assembly_field_after = re.search(r'(?i)Building\s+Height|FM\s+Global|Deck:', after_text)
            
            if has_newline_before or has_assembly_field_after:
                section_markers.append({'name': match.group(1).strip(), 'position': pos})
    
    seen_names = set()
    unique_markers = []
    for marker in sorted(section_markers, key=lambda x: x['position']):
        name_lower = marker['name'].lower()
        if name_lower not in seen_names:
            seen_names.add(name_lower)
            unique_markers.append(marker)
    
    if len(unique_markers) > 1:
        sections = []
        for i, marker in enumerate(unique_markers):
            start = marker['position']
            end = unique_markers[i+1]['position'] if i+1 < len(unique_markers) else len(text)
            sections.append((marker['name'], text[start:end]))
        return sections
    
    return [(None, text)]

def parse_single_assembly_excel_format(text, assembly_name, manufacturer, project_info):
    """Parse single assembly matching Excel template column order."""
    assembly = OrderedDict()
    
    if assembly_name:
        assembly['assembly_roof_area'] = assembly_name
    
    spec_num = extract_spec_number(text)
    if spec_num:
        assembly['spec_number'] = spec_num
    
    assembly['manufacturer'] = manufacturer
    
    system_type = extract_system_type(text)
    if system_type:
        assembly['system'] = system_type
    
    if project_info and 'date' in project_info:
        assembly['date_of_assembly_letter'] = project_info['date']
    
    contractor = extract_contractor(text)
    if contractor:
        assembly['contractor'] = contractor
    
    contractor_addr = extract_contractor_address(text)
    if contractor_addr:
        assembly['contractor_address'] = contractor_addr
    
    if project_info and 'name' in project_info:
        assembly['project_name'] = project_info['name']
    
    if project_info and 'location' in project_info:
        assembly['project_location'] = project_info['location']
    
    roof_height = extract_roof_height(text)
    if roof_height:
        assembly['roof_height'] = roof_height
    
    membranes = extract_membrane_layers(text)
    for i, membrane_data in enumerate(membranes, 1):
        if 'product' in membrane_data:
            assembly[f'membrane_{i}'] = membrane_data['product']
        if 'attachment' in membrane_data:
            assembly[f'membrane_{i}_attachment'] = membrane_data['attachment']
    
    coverboard1 = extract_coverboard(text, 1)
    if coverboard1:
        if 'product' in coverboard1:
            assembly['coverboard_1'] = coverboard1['product']
        if 'attachment' in coverboard1:
            assembly['coverboard_1_attachment'] = coverboard1['attachment']
    
    insulation_layers = extract_insulation_layers_detailed(text)
    for i, insul_data in enumerate(insulation_layers, 1):
        if 'product' in insul_data:
            assembly[f'insulation_layer_{i}'] = insul_data['product']
        if 'attachment' in insul_data:
            assembly[f'insulation_layer_{i}_attachment'] = insul_data['attachment']
    
    vapor = extract_vapor_barrier(text)
    if vapor:
        if 'product' in vapor:
            assembly['vapor_barrier'] = vapor['product']
        if 'attachment' in vapor:
            assembly['vapor_barrier_attachment'] = vapor['attachment']
    
    coverboard2 = extract_coverboard(text, 2)
    if coverboard2:
        if 'product' in coverboard2:
            assembly['coverboard_2'] = coverboard2['product']
        if 'attachment' in coverboard2:
            assembly['coverboard_2_attachment'] = coverboard2['attachment']
    
    deck_slope = extract_deck_slope(text)
    if deck_slope:
        if 'product' in deck_slope:
            assembly['deck_slope'] = deck_slope['product']
        if 'attachment' in deck_slope:
            assembly['deck_slope_attachment'] = deck_slope['attachment']
    
    approvals = extract_approvals_detailed(text)
    for key, value in approvals.items():
        assembly[f'approval_{key}'] = value
    
    return assembly

def extract_spec_number(text):
    """Extract specification number if present."""
    patterns = [
        r'(?i)Spec(?:ification)?\s*(?:Number|No\.?|#)[:\s]+([A-Z0-9\-]+)',
        r'(?i)Project\s+(?:Number|No\.?|#)[:\s]+([A-Z0-9\-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text[:500])
        if match:
            return match.group(1).strip()
    return None

def extract_system_type(text):
    """Extract system type (TPO, PVC, EPDM, etc.)."""
    if re.search(r'(?i)\bTPO\b', text[:1000]):
        return 'TPO'
    if re.search(r'(?i)\bPVC\b', text[:1000]):
        return 'PVC'
    if re.search(r'(?i)\bEPDM\b', text[:1000]):
        return 'EPDM'
    if re.search(r'(?i)SBS|modified\s+bitumen', text[:1000]):
        return 'SBS Modified Bitumen'
    if re.search(r'(?i)built[-\s]?up|BUR', text[:1000]):
        return 'Built-Up'
    return None

def extract_contractor(text):
    """Extract contractor name."""
    patterns = [
        r'(?i)Attn:\s*([^\n]+)',
        r'(?i)Contractor[:\s]+([^\n]+)',
        r'(?i)(?:To|Attention):\s*([A-Z][^\n]{10,80})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text[:500])
        if match:
            contractor = match.group(1).strip()
            contractor = re.sub(r'\d{4,}.*', '', contractor)
            return contractor[:100]
    return None

def extract_contractor_address(text):
    """Extract contractor address."""
    pattern = r'(?i)Attn:[^\n]+\n\s*([^\n]+\n[^\n]+)'
    match = re.search(pattern, text[:800])
    if match:
        address = match.group(1).strip()
        address = re.sub(r'\s+', ' ', address)
        return address[:150]
    return None

def extract_roof_height(text):
    """Extract building/roof height."""
    patterns = [
        r'(?i)Building\s+Height[:\s]+([^\n]+?)(?=\s*FM|\s*Slope|\n)',
        r'(?i)(?:Approximately|Approx\.?)\s+(\d+[\'"\s]*(?:tall|high|feet|ft))',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()[:100]
    return None

def extract_membrane_layers(text):
    """Extract membrane layers (up to 3) with separate product and attachment."""
    membranes = []
    membrane_pattern = r'(?i)(\d+[-\s]?mil[s]?\s+[A-Za-z\-]+\s+(?:TPO|PVC|EPDM|membrane)[^\n.]*)'
    
    for match in re.finditer(membrane_pattern, text):
        membrane_text = match.group(1).strip()
        product, attachment = split_product_attachment(membrane_text)
        membranes.append({'product': product, 'attachment': attachment})
        if len(membranes) >= 3:
            break
    
    return membranes

def extract_coverboard(text, layer_num):
    """Extract coverboard with attachment method."""
    patterns = [
        r'(?i)cover\s*board[:\s]+([^\n]+)',
        r'(?i)gypsum[-\s]fiber\s+roof\s+board[:\s]+([^\n]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            coverboard_text = match.group(1).strip()[:300]
            product, attachment = split_product_attachment(coverboard_text)
            return {'product': product, 'attachment': attachment}
    
    return None

def extract_insulation_layers_detailed(text):
    """Extract insulation layers (up to 3) with separate product and attachment."""
    layers = []
    patterns = [
        r'(?i)(\d+\.?\d*"?\s+thick\s+[A-Za-z]+[^\n]+insulation[^\n.]+)',
        r'(?i)Insulation[:\s]+([^\n]+)',
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            insul_text = match.group(1).strip()[:400]
            insul_text = re.split(r'(?i)\bDeck:', insul_text)[0]
            product, attachment = split_product_attachment(insul_text)
            layers.append({'product': product, 'attachment': attachment})
            if len(layers) >= 3:
                break
        if layers:
            break
    
    return layers

def extract_vapor_barrier(text):
    """Extract vapor barrier/retarder with attachment."""
    patterns = [r'(?i)vapor\s+(?:retarder|barrier)[:\s]+([^\n]+)']
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            vapor_text = match.group(1).strip()[:200]
            product, attachment = split_product_attachment(vapor_text)
            return {'product': product, 'attachment': attachment}
    
    return None

def extract_deck_slope(text):
    """Extract deck and slope information."""
    deck_text = None
    slope_text = None
    
    deck_pattern = r'(?i)Deck[:\s]+([^\n]+?)(?=\s*$|\s*Canopy|\s*Receiving|\n\n)'
    deck_match = re.search(deck_pattern, text)
    if deck_match:
        deck_text = deck_match.group(1).strip()[:150]
    
    slope_pattern = r'(?i)Slope[:\s]+([^\n]+?)(?=\s*Membrane|\s*Building|\n\n)'
    slope_match = re.search(slope_pattern, text)
    if slope_match:
        slope_text = slope_match.group(1).strip()[:200]
    
    combined = []
    if deck_text:
        combined.append(deck_text)
    if slope_text:
        combined.append(f"Slope: {slope_text}")
    
    if combined:
        full_text = '. '.join(combined)
        product, attachment = split_product_attachment(full_text)
        return {'product': product, 'attachment': attachment}
    
    return None

def split_product_attachment(text):
    """Split text into product name and attachment method/specifications."""
    attachment_keywords = [
        'mechanically fastened', 'mechanically attached', 'adhered',
        'torch applied', 'self-adhered', 'fasteners', 'plates',
        'HP-X', 'InsulFast', 'with', 'at 12"', 'on center'
    ]
    
    split_pos = len(text)
    for keyword in attachment_keywords:
        pos = text.lower().find(keyword.lower())
        if pos > 0 and pos < split_pos:
            split_pos = pos
    
    if split_pos < len(text):
        product = text[:split_pos].strip()
        attachment = text[split_pos:].strip()
        return product, attachment if attachment else None
    
    return text, None

def extract_approvals_detailed(text):
    """Extract approvals separately."""
    approvals = OrderedDict()
    
    roofnav = re.search(r'(?i)RoofNav\s*#?\s*([\d\-]+)', text)
    if roofnav:
        approvals['fm_roofnav'] = roofnav.group(1)
    
    fm_listing = re.search(r'(?i)FM\s+Global[®\s]+Listing[:\s]+Reference\s+RoofNav\s*#?\s*([\d\-]+[^\n.]*)', text)
    if fm_listing:
        approvals['fm_global_listing'] = fm_listing.group(1).strip()[:200]
    
    ul_match = re.search(r'(?i)UL\s+(?:Class\s+)?([A-C])', text)
    if ul_match:
        approvals['ul_rating'] = f"Class {ul_match.group(1)}"
    
    astm_matches = re.findall(r'(?i)(ASTM\s+[A-Z][-\d]+)', text)
    if astm_matches:
        approvals['astm_standards'] = ', '.join(set(astm_matches[:5]))
    
    return approvals

def extract_manufacturer(text):
    """Detect manufacturer."""
    manufacturers = {
        'Carlisle': r'(?i)carlisle',
        'Mule-Hide': r'(?i)mule[-\s]?hide',
        'GAF': r'(?i)\bGAF\b',
        'Firestone': r'(?i)firestone',
        'Johns Manville': r'(?i)johns\s+manville',
        'Siplast': r'(?i)siplast',
        'SOPREMA': r'(?i)soprema',
        'Versico': r'(?i)versico',
    }
    
    for name, pattern in manufacturers.items():
        if re.search(pattern, text[:2000]):
            return name
    return 'Unknown'

def extract_project_info(text):
    """Extract project information."""
    info = OrderedDict()
    
    project_patterns = [r'(?i)(?:RE|Re|Subject):\s*([^\n]+)']
    for pattern in project_patterns:
        match = re.search(pattern, text[:1000])
        if match:
            name = match.group(1).strip()
            name = re.sub(r'(?i)\s*[-–]?\s*To\s+Whom\s+[Ii]t\s+May\s+Concern.*', '', name)
            if name:
                info['name'] = name[:150]
                break
    
    location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b', text[:2000])
    if location_match:
        info['location'] = f"{location_match.group(1)}, {location_match.group(2)}"
    
    date_match = re.search(r'([A-Za-z]+\s+\d+,\s+\d{4})', text[:800])
    if date_match:
        info['date'] = date_match.group(1)
    
    return info if info else None