import json
import re
import os

def parse_localization_file(localization_path):
    """
    Parse the localization file to extract translations.
    
    Args:
        localization_path (str): Path to localization file
        
    Returns:
        dict: Dictionary with language mappings and item translations
    """
    localization_data = {
        'languages': [],
        'items': {}
    }
    
    try:
        with open(localization_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        if len(lines) < 2:
            print("Warning: Localization file has insufficient data")
            return localization_data
        
        # First line contains language codes
        lang_line = lines[0].strip()
        languages = [lang.strip() for lang in lang_line.split('\t') if lang.strip()]
        
        # Second line contains language display names
        display_line = lines[1].strip()
        display_names = [name.strip() for name in display_line.split('\t') if name.strip()]
        
        # Create language mapping
        for i, lang_code in enumerate(languages):
            display_name = display_names[i + 1] if i < len(display_names) else lang_code # Shift by 1 to skip the first entry which is technical name
            localization_data['languages'].append({
                'code': lang_code,
                'display_name': display_name
            })
        
        # Parse item translations (skip first 2 lines)
        for line in lines[2:]:
            line = line.strip()
            if not line:
                continue
                
            parts = [part.strip() for part in line.split('\t')]
            if len(parts) < 2:
                continue
                
            key = parts[0]
            translations = parts[1:len(languages)+1]  # Only take as many as we have languages
            
            # Extract item ID and type from key
            if 'item.' in key and ('.name' in key or '.shortdesc' in key):
                item_id = key.replace('.name', '').replace('.shortdesc', '')
                translation_type = 'name' if '.name' in key else 'description'
                
                if item_id not in localization_data['items']:
                    localization_data['items'][item_id] = {}
                
                if translation_type not in localization_data['items'][item_id]:
                    localization_data['items'][item_id][translation_type] = {}
                
                # Map translations to languages
                for i, translation in enumerate(translations):
                    if i < len(languages):
                        lang_code = languages[i]
                        localization_data['items'][item_id][translation_type][lang_code] = translation
        
        print(f"Loaded localization for {len(localization_data['languages'])} languages")
        print(f"Found translations for {len(localization_data['items'])} items")
        
    except FileNotFoundError:
        print(f"Warning: Localization file not found at {localization_path}")
    except Exception as e:
        print(f"Warning: Error parsing localization file: {str(e)}")
    
    return localization_data

def clean_line(headers_line):
    """
    Clean headers line by handling multiple tabs and excess whitespace.
    """
    cleaned_line = re.sub(r'\t+', '\t', headers_line.strip())
    headers = [h.strip() for h in cleaned_line.split('\t') if h.strip()]
    return headers

def parse_config_items(file_path, required_headers=None, localization_data=None):
    """
    Parse config_items.txt file to extract categories with specified headers.
    
    Args:
        file_path (str): Path to the config_items.txt file
        required_headers (list): List of headers that must be present in a category
        localization_data (dict): Localization data from parse_localization_file()
    """
    if required_headers is None:
        required_headers = ['ArmorClass']
    
    matching_categories = {}
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if line starts with # and is not #end
        if line.startswith('#') and not line.startswith('#end'):
            category_name = line[1:].strip()  # Remove # prefix
            category_type = category_name  # Store original category name as type
            i += 1
            
            # Get headers line
            if i < len(lines):
                headers_line = lines[i].strip()
                original_headers = clean_line(headers_line)
                
                # Add "Type" as first header
                headers = ['Type'] + original_headers
                
                print(f"Category: {category_name}")
                print(f"Headers: {headers}")
                print(f"Header count: {len(headers)}")
                
                # Check if all required headers are present in original headers
                has_required_headers = all(header in original_headers for header in required_headers)
                
                if has_required_headers:
                    i += 1
                    category_data = []
                    
                    # Collect data lines until #end or next category
                    while i < len(lines):
                        data_line = lines[i].strip()
                        
                        # Stop if we hit #end or another category
                        if data_line.startswith('#end') or (data_line.startswith('#') and not data_line.startswith('#end')):
                            break
                        
                        # Skip empty lines
                        if data_line:
                            # Clean and split data line
                            values = clean_line(data_line)
                            
                            # Create row dictionary with Type as first field
                            row_dict = {'Type': category_type}
                            
                            # Add other fields
                            for j, header in enumerate(original_headers):
                                if j < len(values):
                                    row_dict[header] = values[j]
                                else:
                                    row_dict[header] = ""
                            
                            # Add localization if available
                            if localization_data and 'Id' in row_dict:
                                item_id = 'item.' + row_dict['Id']

                                if item_id in localization_data['items']:
                                    item_translations = localization_data['items'][item_id]
                                    
                                    # Add name and description for each language
                                    for lang_info in localization_data['languages']:
                                        lang_code = lang_info['code']
                                        lang_display = lang_info['display_name']
                                        
                                        # Add name
                                        if 'name' in item_translations and lang_code in item_translations['name']:
                                            row_dict[f'Name_{lang_display}'] = item_translations['name'][lang_code]
                                        else:
                                            row_dict[f'Name_{lang_display}'] = ""
                                        
                                        # Add description
                                        if 'description' in item_translations and lang_code in item_translations['description']:
                                            row_dict[f'Description_{lang_display}'] = item_translations['description'][lang_code]
                                        else:
                                            row_dict[f'Description_{lang_display}'] = ""
                            
                            category_data.append(row_dict)
                        
                        i += 1
                    
                    # Update headers to include localization headers if they were added
                    if category_data and localization_data:
                        # Get headers from first row to include localization headers
                        headers = list(category_data[0].keys())
                    
                    # Store category data
                    matching_categories[category_name] = {
                        'headers': headers,
                        'required_headers_found': required_headers,
                        'data': category_data
                    }
                    
                    continue
        
        i += 1
    
    return matching_categories

def create_language_specific_data(categories_data, language_display_name):
    """
    Create language-specific dataset with only one language's translations.
    
    Args:
        categories_data (dict): Full categories data with all languages
        language_display_name (str): Display name of language to extract
        
    Returns:
        dict: Data with only specified language translations
    """
    language_data = {}
    
    for category_name, category_info in categories_data.items():
        # Filter headers to include base headers + specific language
        base_headers = [h for h in category_info['headers'] 
                       if not h.startswith('Name_') and not h.startswith('Description_')]
        lang_headers = [h for h in category_info['headers'] 
                       if h.endswith(f'_{language_display_name}')]
        
        # Rename language-specific headers to generic names
        header_mapping = {}
        final_headers = base_headers.copy()
        
        for lang_header in lang_headers:
            if lang_header.startswith('Name_'):
                header_mapping[lang_header] = 'Name'
                if 'Name' not in final_headers:
                    final_headers.append('Name')
            elif lang_header.startswith('Description_'):
                header_mapping[lang_header] = 'Description'
                if 'Description' not in final_headers:
                    final_headers.append('Description')
        
        # Process data rows
        filtered_rows = []
        for row in category_info['data']:
            new_row = {}
            
            # Copy base fields
            for header in base_headers:
                new_row[header] = row.get(header, "")
            
            # Copy and rename language-specific fields
            for old_header, new_header in header_mapping.items():
                new_row[new_header] = row.get(old_header, "")
            
            filtered_rows.append(new_row)
        
        language_data[category_name] = {
            'headers': final_headers,
            'language': language_display_name,
            'data': filtered_rows
        }
    
    return language_data

def filter_data_by_headers(categories_data, selected_headers=None):
    if selected_headers is None:
        return categories_data
    
    filtered_data = {}
    
    for category_name, category_info in categories_data.items():
        available_headers = category_info['headers']
        filtered_headers = [h for h in selected_headers if h in available_headers]
        
        if filtered_headers:
            filtered_rows = []
            for row in category_info['data']:
                filtered_row = {header: row.get(header, "") for header in filtered_headers}
                filtered_rows.append(filtered_row)
            
            filtered_data[category_name] = {
                'headers': filtered_headers,
                'original_headers': available_headers,
                'required_headers_found': category_info.get('required_headers_found', []),
                'data': filtered_rows
            }
    
    return filtered_data

def save_data_to_json(categories_data, output_file='filtered_data.json'):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(categories_data, file, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {output_file}")
    print(f"Found {len(categories_data)} matching categories:")
    for category_name, category_info in categories_data.items():
        print(f"  - {category_name}: {len(category_info['data'])} items")

def main():
    input_file = 'config_items.txt'
    localization_file = f'localization.txt'
    
    # Parse localization data
    print("Loading localization data...")
    localization_data = parse_localization_file(localization_file)
    
    # Configuration options
    config_options = {
        'armor_with_localization': {
            'required_headers': ['ArmorClass'],
            'selected_headers': ['Name', 'Description', 'Type', 'ArmorClass', 'ResistSheet', 'MaxDurability', 'Weight'],
            'output_file': 'armor_data_full.json',
            'use_localization': True,
            'language_filter': 'English'
        },
    }
    
    selected_config = 'armor_with_localization'
    config = config_options[selected_config]
    
    print(f"\nUsing configuration: {selected_config}")
    print(f"Required headers: {config['required_headers']}")
    
    try:
        # Parse the config file
        matching_categories = parse_config_items(
            input_file, 
            required_headers=config['required_headers'],
            localization_data=localization_data if config.get('use_localization') else None
        )
        
        # Apply language filter if specified
        if config.get('language_filter'):
            matching_categories = create_language_specific_data(
                matching_categories, 
                config['language_filter']
            )
        
        # Filter to selected headers
        filtered_data = filter_data_by_headers(
            matching_categories, 
            selected_headers=config['selected_headers']
        )
        
        # Save to JSON
        save_data_to_json(filtered_data, config['output_file'])
        
        # Also create individual language files
        if config.get('use_localization') and not config.get('language_filter'):
            print("\nCreating individual language files...")
            for lang_info in localization_data['languages']:
                lang_name = lang_info['display_name']
                lang_data = create_language_specific_data(matching_categories, lang_name)
                lang_filtered = filter_data_by_headers(
                    lang_data,
                    selected_headers=['Type', 'Id', 'ArmorClass', 'Price', 'Name', 'Description']
                )
                
                lang_filename = f"armor_data_{lang_name.lower().replace(' ', '_')}.json"
                save_data_to_json(lang_filtered, lang_filename)
        
        print(f"\nProcessing complete!")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {str(e)}")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

# def custom_parse_with_localization(input_file, localization_file, required_headers, 
#                                  selected_headers=None, language_filter=None, 
#                                  output_file='output.json'):
#     """
#     Convenience function for custom parsing with localization support.
    
#     Args:
#         input_file (str): Path to config file
#         localization_file (str): Path to localization.txt file
#         required_headers (list): Headers that must be present to include a category
#         selected_headers (list): Headers to keep in output (None = keep all)
#         language_filter (str): Specific language to extract (None = all languages)
#         output_file (str): Output JSON file name
#     """
#     try:
#         # Parse localization data
#         localization_data = parse_localization_file(localization_file)
        
#         # Parse with required headers and localization
#         matching_categories = parse_config_items(
#             input_file, 
#             required_headers, 
#             localization_data
#         )
        
#         # Apply language filter if specified
#         if language_filter:
#             matching_categories = create_language_specific_data(
#                 matching_categories, 
#                 language_filter
#             )
        
#         # Filter to selected headers
#         filtered_data = filter_data_by_headers(matching_categories, selected_headers)
        
#         # Save to JSON
#         save_data_to_json(filtered_data, output_file)
        
#         return filtered_data
        
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None

def debug_localization_file(localization_path, max_items=5):
    """
    Debug function to examine localization file structure.
    """
    print("=== LOCALIZATION FILE DEBUG ===")
    
    try:
        with open(localization_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        print(f"Total lines: {len(lines)}")
        print("\nFirst few lines:")
        for i, line in enumerate(lines[:5]):
            print(f"Line {i+1}: {repr(line.rstrip())}")
        
        print("\nSample item translations:")
        item_count = 0
        for line in lines[2:]:  # Skip header lines
            if '.name' in line or '.shortdesc' in line:
                print(f"  {line.rstrip()}")
                item_count += 1
                if item_count >= max_items:
                    break
                    
    except Exception as e:
        print(f"Error reading localization file: {e}")

if __name__ == "__main__":
    main()
    
    # # Example usage:
    # print("\n" + "="*60)
    # print("EXAMPLE USAGE:")
    
    # # Example 1: Get armor data with English translations only
    # print("\nExample 1: Armor with English translations")
    # custom_parse_with_localization(
    #     'config_items.txt',
    #     'e:/Temp/Quasi/AssetRipper_export_20250604_121357/ExportedProject/Assets/Resources/localization.txt',
    #     required_headers=['ArmorClass'],
    #     selected_headers=['Type', 'Id', 'ArmorClass', 'Price', 'Name', 'Description'],
    #     language_filter='English',
    #     output_file='armor_english_example.json'
    # )
    
    # # Example 2: Get all items with price, include all languages
    # print("\nExample 2: All priced items with all languages")
    # custom_parse_with_localization(
    #     'config_items.txt',
    #     'e:/Temp/Quasi/AssetRipper_export_20250604_121357/ExportedProject/Assets/Resources/localization.txt',
    #     required_headers=['Price'],
    #     selected_headers=['Type', 'Id', 'Price'],  # Will include all Name_* and Description_* fields
    #     language_filter=None,
    #     output_file='priced_items_multilang.json'
    # )

