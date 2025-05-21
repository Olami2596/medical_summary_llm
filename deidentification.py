import re
import spacy

nlp = spacy.load("en_core_web_lg")

def deidentify_patient_info(text):
    if not text or not isinstance(text, str):
        return text
    """
    Remove patient identifying information from medical text
    """
    if not text or not isinstance(text, str):
        return text
    
    # Make a copy of the original text that we'll modify
    deidentified_text = text

    # 1. Replace names and person entities
    doc = nlp(text)
    
    # Track all replacements to ensure consistency
    replacements = {}
    
    # Process named entities
    for ent in doc.ents:
        # Handle person names
        if ent.label_ == "PERSON":
            if ent.text not in replacements:
                replacements[ent.text] = "[PERSON]"
            deidentified_text = deidentified_text.replace(ent.text, replacements[ent.text])
        
        # Handle ages
        elif ent.label_ == "DATE" and re.search(r'\b\d{1,2}[ -]*(years?|yrs?).{0,10}(old|age)\b', ent.text, re.IGNORECASE):
            deidentified_text = deidentified_text.replace(ent.text, "[AGE]")
        
        # Handle locations (addresses, cities)
        elif ent.label_ in ["GPE", "LOC"]:
            if ent.text not in replacements:
                replacements[ent.text] = "[LOCATION]"
            deidentified_text = deidentified_text.replace(ent.text, replacements[ent.text])
    
    # 2. Replace specific patterns

    # Replace age patterns like "51-year-old", "30 yrs old", etc.
    age_patterns = [
        r'\b\d{1,3}[-\s]?(year[-\s]?old|yrs?[-\s]?old|years?[-\s]?of[-\s]?age)\b',  # 51-year-old
        r'\b\d{1,3}\s*(?:y/?o|yo|y\.o\.)\b',  # 37 y/o, 37yo, 37 y.o.
        r'\bage[d\s:]*?(\d{1,3})\b',  # aged 45, age: 45
        r'\b(\d{1,3})[-\s]?years?\b'  # 37 years
    ]
    
    for pattern in age_patterns:
        deidentified_text = re.sub(pattern, '[AGE]', deidentified_text, flags=re.IGNORECASE)
    
    deidentified_text = re.sub(r'\b\d{1,3}\s*[yY]\b', '[AGE]', deidentified_text)

    #  Replace case numbers
    deidentified_text = re.sub(r'\b(?:Case\s+(?:No|Number|#)?[:.\s-]?\s*[A-Z0-9][-A-Z0-9]*)\b', '[CASE_NUMBER]', deidentified_text, flags=re.IGNORECASE)
        
    # Social Security Numbers (XXX-XX-XXXX or XXX XX XXXX)
    deidentified_text = re.sub(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', '[SSN]', deidentified_text)
    
    # Phone numbers (various formats)
    deidentified_text = re.sub(r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE]', deidentified_text)
    deidentified_text = re.sub(r'\b0\d{10}\b', '[PHONE]', deidentified_text)
    deidentified_text = re.sub(r'\b0\d{3,5}[A-Z]+\s*\(\d{10}\)', '[PHONE]', deidentified_text, flags=re.IGNORECASE)
    deidentified_text = re.sub(r'\b0\d{3,5}[A-Z]+\s*\(\d{10}\)', '[PHONE]', deidentified_text, flags=re.IGNORECASE)
    
    # Email addresses
    deidentified_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', deidentified_text)
    
    # Medical record numbers (various formats)
    deidentified_text = re.sub(r'\b(MRN|Medical Record Number|Record Number|Record #|#)[:.\s]?\s*\d+\b', '[MRN]', deidentified_text)
    
    # Enhanced date patterns with additional formats
    date_patterns = [
        # DOB explicit formats
        r'\b(?:DOB|Date of Birth|Birth Date|Born on)[:.\s]?\s*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        r'\b(?:DOB|Date of Birth|Birth Date|Born on)[:.\s]?\s*\w+ \d{1,2},? \d{2,4}\b',
        
        # Date formats - be thorough to catch numeric dates
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # 11/06/08, 06/15/1972
        r'\b\d{2}[-/]\d{2}[-/]\d{2}\b',        # Special case for dates like 11/06/08
        
        # Month name formats
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[.,]?\s+\d{1,2}(?:st|nd|rd|th)?[.,]?\s*\d{2,4}\b',
        
        # Stand-alone months with days
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[.,]?\s+\d{1,2}(?:st|nd|rd|th)?\b',
    ]
    
    for pattern in date_patterns:
        deidentified_text = re.sub(pattern, '[DATE]', deidentified_text, flags=re.IGNORECASE)
    
    # Height measurements - FIXED to completely capture including quote marks
    # Format for height entries (e.g., "Height: 5'10"" or "5 ft 10 in")
    deidentified_text = re.sub(r'\b(height|ht)[:.]\s*\d+\s*(?:\'|feet|ft|foot)?\s*\d*\s*(?:\"|inches|in|″)?', '[HEIGHT]', deidentified_text, flags=re.IGNORECASE)
    
    # Standalone height measurements
    deidentified_text = re.sub(r'\b\d+\s*(?:\'|feet|ft|foot)\s*\d*\s*(?:\"|inches|in|″)?', '[HEIGHT]', deidentified_text, flags=re.IGNORECASE)
    
    # Handle weight more precisely
    deidentified_text = re.sub(r'\b(weight|wt)[:.]\s*\d+\.?\d*\s*(kg|kilos|lb|lbs|pounds)\b', '[WEIGHT]', deidentified_text, flags=re.IGNORECASE)
    deidentified_text = re.sub(r'\b\d+\.?\d*\s*(kg|kilos|lb|lbs|pounds)\b', '[WEIGHT]', deidentified_text, flags=re.IGNORECASE)
    
    # BMI values
    deidentified_text = re.sub(r'\b(BMI|Body Mass Index)[:.]\s*\d+\.?\d*\b', '[BMI]', deidentified_text, flags=re.IGNORECASE)
    deidentified_text = re.sub(r'\bBMI\s+of\s+\d+\.?\d*\b', '[BMI]', deidentified_text, flags=re.IGNORECASE)

    # Address line (e.g., 123 Medical Way)
    address_line_pattern = r'\b\d+\s+(?:[A-Za-z0-9]+\s)*?(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Way|Lane|Ln|Place|Pl|Court|Ct|Terrace|Ter|Circle|Cir)\b'
    deidentified_text = re.sub(address_line_pattern, '[ADDRESS]', deidentified_text, flags=re.IGNORECASE)

    
    # ZIP/Postal codes
    deidentified_text = re.sub(r'\b\d{5}(?:-\d{4})?\b', '[ZIPCODE]', deidentified_text)

    # Enhanced facility identification patterns - FIXED to be more precise
    # Using word boundaries and more precise pattern matching to avoid over-capturing
    facility_patterns = [
        # Pattern to match "Name Hospital" or "Name Medical Center" but not surrounding text
        (r"\b((?:[A-Z][A-Za-z0-9&\-\.'']+\s+)+)(Hospital|Medical Center|Clinic|Infirmary)\b", 
         r"[HOSPITAL]"),
        # Pattern for labs
        (r"\b((?:[A-Z][A-Za-z0-9&\-\.'']+\s+)+)(Laboratory|Lab)\b", 
         r"[LAB]"),
        # Pattern for diagnostic centers
        (r"\b((?:[A-Z][A-Za-z0-9&\-\.'']+\s+)+)(Diagnostic Center|Imaging Center|Diagnostics)\b", 
         r"[DIAGNOSTIC_CENTER]")
    ]
    
    for pattern, replacement in facility_patterns:
        deidentified_text = re.sub(pattern, replacement, deidentified_text)
    
    # Additional catch for standalone facility names without preceding words
    standalone_patterns = [
        (r"\b(Hospital|Medical Center|Clinic|Infirmary)\b", "[HOSPITAL]"),
        (r"\b(Laboratory|Lab)\b", "[LAB]"),
        (r"\b(Diagnostic Center|Imaging Center|Healthcare Limited|Healthcare)\b", "[DIAGNOSTIC_CENTER]")
    ]
    
    for pattern, replacement in standalone_patterns:
        deidentified_text = re.sub(pattern, replacement, deidentified_text, flags=re.IGNORECASE)
    
    # Doctor identification
    doctor_patterns = [
        r"\bDr\.\s+[A-Z][a-z]+\b",
        r"\bDoctor\s+[A-Z][a-z]+\b",
        r"\b[A-Z][a-z]+,\s+M\.?D\.?\b",
        r"\bM\.?D\.?\s+[A-Z][a-z]+\b"
    ]
    
    for pattern in doctor_patterns:
        deidentified_text = re.sub(pattern, "[PHYSICIAN]", deidentified_text)
    
    # Year patterns - identify and replace years
    # Years in context (diagnosed in 2018, treated in 2020, etc.)
    deidentified_text = re.sub(r'\b(in|since|from|during|after|before|circa|around|about|by|until|till|to)\s+\d{4}\b', r'\1 [YEAR]', deidentified_text, flags=re.IGNORECASE)
    
    # Years by themselves (commonly 4-digit years from 1900-2030)
    deidentified_text = re.sub(r'\b(19[0-9][0-9]|20[0-2][0-9]|203[0-5])\b', '[YEAR]', deidentified_text)
    
    # Seasons with years
    deidentified_text = re.sub(r'\b(spring|summer|fall|winter|autumn)\s+of\s+\d{4}\b', r'\1 of [YEAR]', deidentified_text, flags=re.IGNORECASE)
    
    # Months with years
    month_pattern = r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)'
    deidentified_text = re.sub(f'{month_pattern}\\s+\\d{{4}}\\b', r'\1 [YEAR]', deidentified_text, flags=re.IGNORECASE)

    # Time patterns (12-hour and 24-hour formats)
    time_patterns = [
        r'\b(1[0-2]|0?[1-9]):[0-5][0-9]\s*(am|pm|AM|PM|a\.m\.|p\.m\.)\b',  # 12-hour format (3:45 PM)
        r'\b([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?\b'                # 24-hour format (15:45)
    ]

    for pattern in time_patterns:
        deidentified_text = re.sub(pattern, '[TIME]', deidentified_text)

    # Website URLs
    deidentified_text = re.sub(r'\bhttps?://[^\s]+\b', '[WEBSITE]', deidentified_text)
    deidentified_text = re.sub(r'\bwww\.[^\s]+\b', '[WEBSITE]', deidentified_text)
    deidentified_text = re.sub(r'\b[a-zA-Z0-9-]+\.(com|org|net|edu|gov|co|io|us|uk|ca|au)[^\s]*\b', '[WEBSITE]', deidentified_text)

    # Visit ID patterns - updated to handle various spacing around separators
    deidentified_text = re.sub(r'\bVisit\s+(?:ID|Id|id|#)?(?:\s*[:.\s-]\s*)\d+\b', '[VISIT_ID]', deidentified_text, flags=re.IGNORECASE)
    deidentified_text = re.sub(r'\bVisit\s+(?:ID|Id|id|#)?(?:\s*[:.\s-]\s*)[A-Z0-9][-A-Z0-9]*\b', '[VISIT_ID]', deidentified_text, flags=re.IGNORECASE)

    # Complex address patterns (industrial areas, compounds, plots)
    complex_address_patterns = [
        # Pattern for industrial addresses with plot numbers, blocks, etc.
        r'\b(?:[A-Za-z0-9]+\s+)+(?:Industries|Industrial|Compound|Plaza|Complex)(?:\s*,\s*Plot\s+(?:No\.?|Number)?\s*[-:.]?\s*[A-Za-z0-9-]+)?(?:\s*,\s*Block\s+[A-Za-z0-9-]+)?(?:\s*,\s*[A-Za-z0-9\s]+(?:Industrial|Business|Commercial|Estate|Scheme|Area|Zone))?(?:\s*,\s*[A-Za-z\s]+)?(?:\s*,\s*[A-Za-z]+)?\b',
        
        # Pattern for plot numbers with block designations
        r'\bPlot\s+(?:No\.?|Number)?\s*[-:.]?\s*[A-Za-z0-9-]+(?:\s*,\s*Block\s+[A-Za-z0-9-]+)?\b',
    ]

    for pattern in complex_address_patterns:
        deidentified_text = re.sub(pattern, '[COMPLEX_ADDRESS]', deidentified_text, flags=re.IGNORECASE)
    
    return deidentified_text


