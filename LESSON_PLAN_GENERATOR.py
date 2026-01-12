import json
import re

def clean_and_parse_json(raw_json_string):
    """
    Clean and parse a potentially malformed JSON string.
    """
    try:
        # Try parsing the original string first
        parsed = json.loads(raw_json_string)
        print("✓ JSON parsed successfully on first attempt")
        return parsed
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing error: {e}")
        print(f"  Position: line {e.lineno}, column {e.colno}")
        
        # Clean the JSON string
        cleaned_json = clean_json_string(raw_json_string)
        
        try:
            # Try parsing the cleaned version
            parsed = json.loads(cleaned_json)
            print("✓ JSON parsed successfully after cleaning")
            return parsed
        except json.JSONDecodeError as e2:
            print(f"✗ Still unable to parse after cleaning: {e2}")
            # Try a more aggressive fix
            fixed_json = fix_json_structure(cleaned_json)
            try:
                parsed = json.loads(fixed_json)
                print("✓ JSON parsed successfully after structure fix")
                return parsed
            except json.JSONDecodeError as e3:
                print(f"✗ Failed to fix JSON: {e3}")
                return None

def clean_json_string(json_string):
    """
    Remove control characters and fix common JSON issues.
    """
    # Remove control characters (except tabs in string values)
    # First, let's find and visualize problematic characters
    print("\nAnalyzing problematic characters:")
    for i, char in enumerate(json_string[:50]):  # Check first 50 chars
        if ord(char) < 32 and char != '\n' and char != '\t' and char != '\r':
            print(f"  Position {i}: Control character {ord(char)}")
    
    # Remove common problematic control characters
    # Keep \t, \n, \r for string content but remove others
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_string)
    
    # Replace single quotes with double quotes for JSON compliance
    # But be careful with apostrophes inside strings
    # Simple approach: replace ' with " when it's at string boundaries
    cleaned = re.sub(r"(?<=\s|^|:)'(.*?)'(?=\s|$|,|})", r'"\1"', cleaned)
    
    # Fix unclosed quotes at the end
    if cleaned.count('"') % 2 != 0:
        # Add missing quote at the end
        cleaned = cleaned.rstrip() + '"'
    
    # Ensure proper termination
    if not cleaned.strip().endswith('}'):
        cleaned = cleaned.rstrip()
        if not cleaned.endswith('"'):
            cleaned += '"'
        cleaned += '}'
    
    # Fix the specific issue from the example
    if "'" in cleaned and cleaned.endswith(",'"):
        cleaned = cleaned[:-2] + '"'
    
    print(f"\nCleaned JSON string: {cleaned}")
    return cleaned

def fix_json_structure(json_string):
    """
    Attempt to fix JSON structure issues.
    """
    # Trim whitespace
    json_string = json_string.strip()
    
    # Ensure it starts with { and ends with }
    if not json_string.startswith('{'):
        json_string = '{' + json_string
    if not json_string.endswith('}'):
        json_string = json_string + '}'
    
    # Fix key-value pairs
    # Look for patterns like "key": 'value' and fix quotes
    json_string = re.sub(r'":\s*\'(.*?)\'(?=\s*[,}])', r'": "\1"', json_string)
    
    # Fix missing commas between items
    json_string = re.sub(r'"\s*"', '", "', json_string)
    
    return json_string

def validate_json_structure(parsed_json):
    """
    Validate the structure of the parsed JSON.
    """
    if not parsed_json:
        return False
    
    print("\nValidating JSON structure:")
    
    # Check if it's a dictionary
    if not isinstance(parsed_json, dict):
        print("✗ JSON is not a dictionary/object")
        return False
    
    # Check for required keys or structure
    print(f"✓ JSON is a valid dictionary with {len(parsed_json)} key(s)")
    
    for key, value in parsed_json.items():
        print(f"  Key: '{key}' => Type: {type(value).__name__}")
        if isinstance(value, str):
            print(f"       Value preview: {value[:50]}...")
    
    return True

def main():
    """Main function to demonstrate JSON parsing and fixing."""
    
    # The problematic JSON from your example
    raw_response = '''{"obj_1": "• Define angles of elevation and angles of depression", '''
    
    print("=" * 60)
    print("JSON PARSING DEMONSTRATION")
    print("=" * 60)
    
    print(f"\nOriginal raw response:\n{raw_response}")
    
    # Clean and parse the JSON
    parsed_json = clean_and_parse_json(raw_response)
    
    if parsed_json:
        # Validate the structure
        is_valid = validate_json_structure(parsed_json)
        
        if is_valid:
            print("\n" + "=" * 60)
            print("FINAL PARSED JSON:")
            print("=" * 60)
            print(json.dumps(parsed_json, indent=2))
            print("\n✓ Successfully parsed and validated JSON!")
            
            # Example of using the parsed data
            print("\n" + "=" * 60)
            print("EXTRACTED CONTENT:")
            print("=" * 60)
            for key, value in parsed_json.items():
                print(f"{key}: {value}")
        else:
            print("\n✗ JSON structure validation failed")
    else:
        print("\n✗ Failed to parse JSON")

    print("\n" + "=" * 60)
    print("ADDITIONAL EXAMPLES")
    print("=" * 60)
    
    # Test with other problematic JSON examples
    test_cases = [
        # Original test case
        '''{"obj_1": "• Define angles of elevation and angles of depression", ''',
        
        # JSON with control characters
        '{"obj_1": "• Define angles\rof elevation", "obj_2": "Solve problems"}',
        
        # JSON with single quotes
        "{'obj_1': 'Define angles', 'obj_2': 'Solve problems'}",
        
        # Well-formed JSON
        '{"obj_1": "Define angles of elevation", "obj_2": "Define angles of depression"}',
    ]
    
    for i, test_json in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_json[:50]}...")
        result = clean_and_parse_json(test_json)
        if result:
            print(f"Parsed: {json.dumps(result, indent=2)}")

def create_valid_json_example():
    """
    Create a properly formatted JSON example.
    """
    valid_json = {
        "obj_1": "• Define angles of elevation and angles of depression",
        "obj_2": "• Solve problems involving angles of elevation and depression",
        "obj_3": "• Apply trigonometric ratios to real-world situations",
        "obj_4": "• Distinguish between angle of elevation and angle of depression"
    }
    
    print("\n" + "=" * 60)
    print("PROPERLY FORMATTED JSON EXAMPLE:")
    print("=" * 60)
    print(json.dumps(valid_json, indent=2))
    
    # Save to file
    with open('lesson_objectives.json', 'w', encoding='utf-8') as f:
        json.dump(valid_json, f, indent=2, ensure_ascii=False)
    
    print("\n✓ Saved to 'lesson_objectives.json'")

if __name__ == "__main__":
    main()
    create_valid_json_example()
