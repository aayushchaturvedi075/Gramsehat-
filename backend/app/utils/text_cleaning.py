import re

def clean_ocr_text(raw_text: str) -> str:
    """
    Performs deterministic, non-LLM text cleaning on OCR output.
    Cleans up noise commonly produced when reading printed/handwritten 
    medical reports and prescriptions in Hindi and English.
    
    Steps:
    1. Replaces non-standard whitespace characters (tabs, non-breaking spaces).
    2. Strips leading/trailing whitespace from each line.
    3. Removes lines containing only stray punctuation or noise characters.
    4. Condenses consecutive spaces within lines.
    5. Condenses excessive consecutive blank lines into at most one blank line.
    6. Trims leading and trailing empty lines from the overall document.
    """
    if not raw_text or not raw_text.strip():
        return ""

    # Replace common non-standard whitespace (NBSP, tabs, etc.) with standard space
    text = raw_text.replace("\u00a0", " ").replace("\t", " ")
    
    lines = text.splitlines()
    cleaned_lines = []
    
    # Stray noise characters pattern (isolated punctuation characters like ~ | _ ^ ` ')
    noise_pattern = re.compile(r"^[\s~|_^`\'\"—\-*+=:;<>\[\]{}]+$")

    for line in lines:
        # Strip trailing and leading whitespace
        trimmed = line.strip()
        
        # If line is empty, keep single empty line placeholder for paragraph spacing
        if not trimmed:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
            
        # Filter out lines that are purely noisy isolated punctuation
        if len(trimmed) <= 3 and noise_pattern.match(trimmed):
            continue
            
        # Condense multiple internal spaces into a single space
        condensed = re.sub(r" {2,}", " ", trimmed)
        
        # Fix spacing around common punctuation like colons (e.g., 'BP : 120/80' -> 'BP: 120/80')
        condensed = re.sub(r"\s+([:;,])", r"\1", condensed)
        
        cleaned_lines.append(condensed)

    # Join and trim any extra blank lines at beginning/end
    result = "\n".join(cleaned_lines).strip()
    return result
