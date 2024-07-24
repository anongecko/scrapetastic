from trafilatura import extract

def extract_content(response, custom_rules):
    extracted_text = extract(response.text)
    
    # Apply custom extraction rules if provided
    if custom_rules:
        # Implement custom rule application logic here
        pass

    return extracted_text