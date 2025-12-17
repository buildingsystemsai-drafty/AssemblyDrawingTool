import re

def clean_rtf_text(text):
    """
    Remove RTF formatting codes and clean up text
    """
    # Remove RTF control words
    text = re.sub(r'\\[a-z]+\d*\s?', '', text)
    
    # Remove hex codes
    text = re.sub(r"\\\'[0-9a-f]{2}", '', text)
    
    # Remove curly braces
    text = text.replace('{', '').replace('}', '')
    
    # Remove asterisks that appear with control codes
    text = re.sub(r'\\\*', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove any remaining backslashes
    text = text.replace('\\', '')
    
    return text.strip()

def deduplicate_list(items):
    """
    Remove duplicate items while preserving order
    """
    seen = set()
    result = []
    for item in items:
        item_lower = item.lower()
        if item_lower not in seen:
            seen.add(item_lower)
            result.append(item)
    return result


def extract_text_from_file(path):
    """Try to extract text from a file path. Uses pdfplumber for PDFs, otherwise reads text file.
    Returns cleaned text string.
    """
    text = ''
    try:
        # Try PDF extraction with pdfplumber
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ''
                text += page_text + '\n'
    except Exception:
        try:
            # Fallback to text file reading
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                text = fh.read()
        except Exception:
            text = ''

    # Clean simple RTF artifacts if present
    if text.strip().startswith('{\\rtf'):
        text = clean_rtf_text(text)

    # Final whitespace normalization
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_items(text, patterns, max_length=120):
    """Run a list of regex patterns against text and return matched snippets up to max_length."""
    items = []
    for pat in patterns:
        try:
            for m in re.finditer(pat, text, re.I):
                s = m.group(0).strip()
                if len(s) > max_length:
                    s = s[:max_length].rsplit(' ', 1)[0]
                items.append(s)
        except re.error:
            continue
    return items


def extract_r_values(text):
    """Extract R-values (e.g., R-20, R 20) from text and return as list."""
    r_vals = []
    for m in re.finditer(r'R[-\s]?(\d{1,3})', text, re.I):
        r_vals.append('R-' + m.group(1))
    return r_vals


def extract_summary(text, max_length=400):
    """Return the first max_length characters as a cleaned summary."""
    s = text.strip()
    if len(s) <= max_length:
        return s
    return s[:max_length].rsplit(' ', 1)[0] + '...'