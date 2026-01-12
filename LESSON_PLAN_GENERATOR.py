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
    # Fixed regex pattern - simpler and more reliable approach
    # First, handle the specific case from your example
    if "'" in cleaned:
        # Pattern to match single-quoted strings that should be double-quoted
        # This matches patterns like: 'text' that follow a colon or comma
        pattern = r"(?<=[:{,\s])'(.*?)'(?=[,\s\]}])"
        cleaned = re.sub(pattern, r'"\1"', cleaned)
    
    # Fix unclosed quotes at the end
    if cleaned.count('"') % 2 != 0:
        # Add missing quote at the end
        cleaned = cleaned.rstrip() + '"'
    
    # Ensure proper termination
    if not cleaned.strip().endswith('}'):
        cleaned = cleaned.rstrip()
        # Remove trailing comma if present
        if cleaned.endswith(','):
            cleaned = cleaned[:-1]
        # Add closing brace
        cleaned += '}'
    
    print(f"\nCleaned JSON string: {cleaned[:100]}...")  # Show first 100 chars
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
    
    # Fix key-value pairs - simpler approach
    # Convert single-quoted strings to double-quoted
    # This handles patterns like: key: 'value'
    import json
    try:
        # Try using json.loads with object_hook or custom parsing
        # For simplicity, use eval with caution (only for trusted input)
        # But better to use a safer approach:
        
        # Manual replacement for common patterns
        replacements = [
            (r":\s*'([^']*)'(?=\s*[,}])", r': "\1"'),
            (r"'([^']*)'(?=\s*:)", r'"\1"'),
        ]
        
        for pattern, replacement in replacements:
            json_string = re.sub(pattern, replacement, json_string)
            
    except Exception as e:
        print(f"Warning in fix_json_structure: {e}")
    
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

def safe_json_parse(raw_response):
    """
    A safer, simpler function to parse JSON with error handling.
    Use this as the main function to call.
    """
    if not raw_response or not isinstance(raw_response, str):
        return None
    
    # First try direct parsing
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        pass
    
    # Try to fix common issues
    fixed = raw_response
    
    # Fix the specific issue from your example
    if fixed.endswith(", '"):
        fixed = fixed[:-3] + '"'
    
    # Ensure it ends with }
    if not fixed.strip().endswith('}'):
        fixed = fixed.strip()
        if fixed.endswith(','):
            fixed = fixed[:-1]
        fixed += '}'
    
    # Replace problematic single quotes
    fixed = fixed.replace(", '", ', "').replace("{'", '{"').replace("':", '":')
    
    # Try parsing again
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed after fixes: {e}")
        # Last resort: try to extract JSON-like content
        match = re.search(r'\{.*\}', fixed, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return None

# Main function for your Streamlit app
def main():
    """Main function for Streamlit app integration."""
    # Example from your error
    raw_response = '''{"obj_1": "• Define angles of elevation and angles of depression", '''
    
    print("Parsing JSON response...")
    
    # Use the safer function
    parsed_json = safe_json_parse(raw_response)
    
    if parsed_json:
        print("Successfully parsed JSON!")
        print(f"Content: {parsed_json}")
        return parsed_json
    else:
        print("Failed to parse JSON")
        
        # Alternative: Create a valid JSON from the string
        print("\nCreating valid JSON from string content...")
        
        # Extract the objective text
        match = re.search(r'"([^"]+)"', raw_response)
        if match:
            objective_text = match.group(1)
            valid_json = {
                "obj_1": objective_text
            }
            print(f"Created valid JSON: {valid_json}")
            return valid_json
    
    return {"error": "Could not parse JSON"}

if __name__ == "__main__":
    # For testing
    result = main()
    print(f"\nFinal result: {result}")
