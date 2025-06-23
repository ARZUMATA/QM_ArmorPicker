import gradio as gr
import json
import pandas as pd
from typing import Dict, List, Any, Tuple
import math
from languages import translations

class ArmorPicker:
    def __init__(self):
        self.resistance_types = ["blunt", "pierce", "lacer", "fire", "cold", "poison", "shock", "beam"]
        self.current_language = "English"
        self.current_version = "0.9"  # Default version
        self.armor_data = {}

        # Color gradient configuration
        self.color_stops = [
            (0.0, "#F8696B"),   # Red at 0%
            (0.3, "#FED280"),   # Orange at 30%
            (0.6, "#C0D980"),   # Yellow at 60%
            (1.0, "#63BE7B")    # Green at 100%
        ]

        # Language configuration
        self.base_languages = {
            "English": {"code": "english", "file": "armor_data_english.json"},
            "Русский": {"code": "russian", "file": "armor_data_russian.json"},
            "Deutsch": {"code": "german", "file": "armor_data_german.json"},
            "Français": {"code": "french", "file": "armor_data_frenсh.json"},
            "Español": {"code": "spanish", "file": "armor_data_spanish.json"},
            "Polski": {"code": "polish", "file": "armor_data_polish.json"},
            "Türkçe": {"code": "turkish", "file": "armor_data_turkish.json"},
            "Português Brasileiro": {"code": "brazilian", "file": "armor_data_brazilianportugal.json"},
            "한국어": {"code": "korean", "file": "armor_data_korean.json"},
            "日本": {"code": "japanese", "file": "armor_data_japanese.json"},
            "中国人": {"code": "chinese", "file": "armor_data_chinesesimp.json"}
        }
        
        self.translations = translations
        
        # Initialize languages for default version
        self.languages = self.get_version_languages(self.current_version)

        # Load default language data
        self.load_armor_data("English")
    
    def get_version_languages(self, version: str) -> Dict:
        """Get language configuration for specific version"""
        version_languages = {}
        for lang_name, lang_config in self.base_languages.items():
            version_languages[lang_name] = {
                "code": lang_config["code"],
                "file": f"versions/{version}/{lang_config['file']}"
            }
        return version_languages
    
    def change_version(self, version: str) -> str:
            """Handle version change and reload language configuration"""
            if version != None:
                self.current_version = version
                self.languages = self.get_version_languages(version)
            # Reload current language data with new version
            self.load_armor_data(self.current_language)
            return f"<p>{self.get_translation('click_search')}</p>"

    def load_armor_data(self, language: str) -> Dict:
        """Load armor data from JSON file for specified language"""
        if language not in self.languages:
            language = "English"
        
        file_path = self.languages[language]["file"]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.armor_data = json.load(f)
                self.current_language = language
                return self.armor_data
        except FileNotFoundError:
            # Fallback to English if file not found
            if language != "English":
                return self.load_armor_data("English")
            else:
                self.armor_data = {"armors": {"data": []}}
                return self.armor_data
    
    def get_translation(self, key: str) -> str:
        """Get translation for current language"""
        return self.translations.get(self.current_language, self.translations["English"]).get(key, key)
    
    def get_armor_types(self) -> List[str]:
        """Get unique armor types from the data"""
        armor_types = set()
        for armor in self.armor_data.get("armors", {}).get("data", []):
            armor_types.add(armor.get("Type", "Unknown"))
        return sorted(list(armor_types))
    
    def filter_armors(self, resistance_filters: Dict[str, Dict]) -> List[Dict]:
        """Filter armors based on resistance requirements"""
        filtered_armors = []
        
        # Dynamically get all armor categories from the data
        for category_name, category_content in self.armor_data.items():
            # Skip if this isn't a category with armor data
            if not isinstance(category_content, dict) or "data" not in category_content:
                continue
                
            category_data = category_content.get("data", [])
            
            for armor in category_data:
                meets_requirements = True
                
                # Check each resistance requirement
                for resist_type, filter_config in resistance_filters.items():
                    if not filter_config["enabled"]:
                        continue
                    
                    required_value = filter_config["value"]
                    
                    # Skip if required_value is None or empty
                    if required_value is None:
                        continue
                    
                    # Convert to int if it's a string, default to 0 if conversion fails
                    try:
                        required_value = int(required_value)
                    except (ValueError, TypeError):
                        required_value = 0
                    
                    armor_resist_value = 0
                    
                    # Find the resistance value in armor's ResistSheet
                    for resist in armor.get("ResistSheet", []):
                        if resist.get("ResistType") == resist_type:
                            armor_resist_value = resist.get("ResistValue", 0)
                            break
                    
                    # Check if armor meets minimum requirement
                    if armor_resist_value < required_value:
                        meets_requirements = False
                        break
                
                if meets_requirements:
                    # Add category information to the armor data for better identification
                    armor_with_category = armor.copy()
                    armor_with_category["Category"] = category_name
                    filtered_armors.append(armor_with_category)
        
        return filtered_armors
    
    def sort_armors(self, armors: List[Dict], sort_by: str, sort_order: str) -> List[Dict]:
        """Sort armors by specified column and order"""
        if not armors or not sort_by:
            return armors
        
        def get_sort_value(armor, column):
            """Get the value to sort by for a given column"""
            if column == "name":
                return armor.get('Name', '').lower()
            elif column == "type":
                return armor.get('Type', '').lower()
            elif column == "durability":
                try:
                    return int(armor.get('MaxDurability', 0))
                except (ValueError, TypeError):
                    return 0
            elif column == "weight":
                try:
                    return float(armor.get('Weight', 0))
                except (ValueError, TypeError):
                    return 0.0
            elif column in self.resistance_types:
                # Find resistance value
                for resist in armor.get("ResistSheet", []):
                    if resist.get("ResistType") == column:
                        return resist.get("ResistValue", 0)
                return 0
            else:
                return ""
        
        # Sort the armors
        reverse = (sort_order == "desc")
        try:
            sorted_armors = sorted(armors, key=lambda x: get_sort_value(x, sort_by), reverse=reverse)
            return sorted_armors
        except Exception:
            # If sorting fails, return original list
            return armors

    def find_armor_combinations(self, resistance_filters: Dict[str, Dict], language: str = None, invincible_perk: bool = False, hardened_talent: bool = False, hardened_talent_lvl: int = 1) -> str:
        """Find armor combinations that meet resistance requirements"""
        if language and language != self.current_language:
            self.load_armor_data(language)
        
        # Get enabled resistance requirements
        enabled_requirements = {}
        for resist_type, filter_config in resistance_filters.items():
            if filter_config["value"] == None: # If NoneType as we have nothing in the input
                filter_config["value"] = 0
            if filter_config["enabled"] and filter_config["value"] > 0:
                enabled_requirements[resist_type] = filter_config["value"]
        
        if not enabled_requirements:
            return f"<p>{self.get_translation('no_requirements_set')}</p>"
        
        # Get all armors grouped by type
        armor_by_type = {}
        for category_name, category_content in self.armor_data.items():
            if not isinstance(category_content, dict) or "data" not in category_content:
                continue
                
            for armor in category_content.get("data", []):
                armor_type = armor.get("Type", "Unknown")
                if armor_type not in armor_by_type:
                    armor_by_type[armor_type] = []
                armor_with_category = armor.copy()
                armor_with_category["Category"] = category_name
                armor_by_type[armor_type].append(armor_with_category)
        
        # Find best armor combinations
        combinations = []
        armor_types = list(armor_by_type.keys())
        
        # Generate combinations (one armor per type)
        from itertools import product
        
        # Limit combinations to prevent performance issues
        max_combinations_per_type = 5
        limited_armor_by_type = {}
        for armor_type, armors in armor_by_type.items():
            # Sort by total resistance for enabled requirements
            def get_total_enabled_resistance(armor):
                total = 0
                for resist in armor.get("ResistSheet", []):
                    resist_type = resist.get("ResistType")
                    if resist_type in enabled_requirements:
                        total += resist.get("ResistValue", 0)
                return total
            
            sorted_armors = sorted(armors, key=get_total_enabled_resistance, reverse=True)
            limited_armor_by_type[armor_type] = sorted_armors[:max_combinations_per_type]
        
        # Generate all possible combinations
        if len(limited_armor_by_type) > 1:
            armor_lists = list(limited_armor_by_type.values())
            for combination in product(*armor_lists):
                combo_score = self.evaluate_combination(combination, enabled_requirements, invincible_perk, hardened_talent, hardened_talent_lvl)
                combinations.append({
                    'armors': combination,
                    'score': combo_score
                })
        
        # Sort combinations by quality (best matches first)
        # Now includes dispersion: lower dispersion (more balanced) is better
        combinations.sort(key=lambda x: (
            -x['score']['dispersion'],       # Lower dispersion is better (more balanced)
             x['score']['avg_coverage'],      # Higher coverage is better
            -x['score']['variance']          # Lower variance is better
        ), reverse=True)
        
        # Filter combinations that meet threshold, but keep at least one
        good_combinations = [combo for combo in combinations if combo['score']['meets_threshold']]
        
        if good_combinations:
            # Use combinations that meet the threshold
            final_combinations = good_combinations[:20]
        elif combinations:
            # No combinations meet threshold, but return the best match(es)
            final_combinations = combinations[:5]  # Return top 5 best matches even if they don't meet requirements
        else:
            # This should rarely happen, but handle the edge case
            return f"<p>{self.get_translation('no_combinations_found')}</p>"
        
        # Create HTML table for combinations
        return self.create_combinations_table_html(final_combinations, enabled_requirements)

    def calculate_resulting_resistance(self, total_armor_score: int) -> float:
        """Calculate resulting resistance percentage using the formula"""
        if total_armor_score <= 0:
            return 0.0
        
        try:
            # 1 - 1.75^(-0.035 * v_armor)
            result = 1 - math.pow(1.75, -0.035 * total_armor_score)
            return max(0.0, min(1.0, result)) # Clamp between 0 and 1
        except (OverflowError, ValueError):
            # Handle edge cases where calculation might fail
            return 1.0 if total_armor_score > 100 else 0.0
        
    def evaluate_combination(self, armor_combination, requirements: Dict[str, int], invincible_perk: bool = False, hardened_talent: bool = False, hardened_talent_lvl: int = 1) -> Dict:
        """Evaluate how well an armor combination meets requirements using resistance formula"""
        total_armor_scores = {}
        
        # Calculate total armor score for each resistance type
        for armor in armor_combination:
            for resist in armor.get("ResistSheet", []):
                resist_type = resist.get("ResistType")
                resist_value = resist.get("ResistValue", 0)
                
                total_armor_scores[resist_type] = total_armor_scores.get(resist_type, 0) + resist_value
        
        # Apply perks to the total combined resistance scores
        for resist_type in total_armor_scores:
            # Apply Invincible perk: +12 to all resistances
            if invincible_perk:
                total_armor_scores[resist_type] = total_armor_scores[resist_type] + 12
            
            # Apply Hardened talent: +10% to resistances
            if hardened_talent:
                resistance_increase = {
                    1: 1.1,   # +10%
                    2: 1.2,   # +20%
                    3: 1.3,   # +30%
                    4: 1.4    # +40%
                }
                
                total_armor_scores[resist_type] = total_armor_scores[resist_type] * resistance_increase.get(hardened_talent_lvl, 1)
        
        # Calculate resulting resistance percentages and coverage
        resulting_resistances = {}
        coverages = []
        enabled_resistance_percentages = []  # For dispersion calculation
        
        for resist_type, required_percentage in requirements.items():
            total_score = total_armor_scores.get(resist_type, 0)
            resulting_resistance = self.calculate_resulting_resistance(total_score)
            resulting_percentage = resulting_resistance * 100  # Convert to percentage
            
            resulting_resistances[resist_type] = {
                'score': total_score,
                'percentage': resulting_percentage
            }
            
            # Store for dispersion calculation
            enabled_resistance_percentages.append(resulting_percentage)
            
            # Calculate coverage (how well we meet the requirement)
            # Required percentage should be treated as the target resistance percentage
            required_decimal = required_percentage / 100.0 if required_percentage > 1 else required_percentage
            coverage = min(resulting_resistance / required_decimal, 1.0) if required_decimal > 0 else 1.0
            coverages.append(coverage)
        
        # Calculate dispersion (standard deviation of resistance percentages)
        # Lower dispersion = more balanced protection, Higher dispersion = uneven protection
        dispersion = 0.0
        
        # Only calculate dispersion if we have more than one resistance type enabled
        if len(enabled_resistance_percentages) > 1:
            mean_percentage = sum(enabled_resistance_percentages) / len(enabled_resistance_percentages)
            variance = sum((percentage - mean_percentage) ** 2 for percentage in enabled_resistance_percentages) / (len(enabled_resistance_percentages)-1)
            dispersion = variance ** 0.5  # Standard deviation
        
        # Calculate metrics
        avg_coverage = sum(coverages) / len(coverages) if coverages else 0
        variance = sum((c - avg_coverage) ** 2 for c in coverages) / len(coverages) if coverages else 0
        meets_threshold = avg_coverage >= 0.9  # At least 90% of requirements met
        
        return {
            'avg_coverage': avg_coverage,
            'variance': variance,
            'meets_threshold': meets_threshold,
            'total_armor_scores': total_armor_scores,  # Keep for backward compatibility
            'resulting_resistances': resulting_resistances,  # New: actual resistance percentages
            'coverages': coverages,
            'dispersion': dispersion,  # New: resistance flatness measure
            'mean_resistance': sum(enabled_resistance_percentages) / len(enabled_resistance_percentages) if enabled_resistance_percentages else 0
        }

    def create_combinations_table_html(self, combinations: List[Dict], requirements: Dict[str, int]) -> str:
        """Create HTML table for armor combinations with CSS custom properties"""
        
        html = f"""
        <style>
        .combo-table {{
            border-collapse: collapse !important;
            width: 100% !important;
            font-size: 16px !important;
            margin-bottom: 20px !important;
        }}
        .combo-table th, .combo-table td {{
            border: 1px solid #000 !important;
            padding: 8px !important;
            background-color: #333 !important;
        }}
        .combo-table th {{
            background-color: #555 !important;
            font-weight: bold !important;
        }}
        .combo-summary {{
            font-weight: bold !important;
            background-color: #2a2a2a !important;
        }}
        .combo-summary .combo-name {{
            text-align: right !important;
        }}
        .combo-detail {{
            padding-left: 20px !important;
            font-style: bold !important;
        }}
        .combo-score-summary {{
            font-weight: bold !important;
            background-color: #444 !important;
            font-style: italic !important;
        }}
        .combo-separator {{
            background-color: transparent !important;
            border: 1px solid transparent !important;
        }}
        .combo-separator td {{
            background-color: transparent !important;
            border: transparent !important;
            padding: 8px !important;
            height: 16px !important;
        }}
        .dispersion-cell {{
            font-weight: bold !important;
            text-align: left !important;
            color: #000 !important;
        }}
        .summary-resist-cell {{
            font-weight: bold !important;
            text-align: left !important;
            color: #000 !important;
        }}
        .armor-resist-cell {{
            text-align: right !important;
            background-color: #333 !important;
            color: #fff !important;
        }}
        .result-resist-cell {{
            font-weight: bold !important;
            text-align: left !important;
            background-color: #444 !important;
        }}
        .mean-cell {{
            font-weight: bold !important;
            text-align: left !important;
            background-color: #444 !important;
            color: #fff !important;
            font-style: italic !important;
        }}
        
        .dispersion-colored {{
            color: var(--dispersion-color) !important;
        }}
        .diff-colored {{
            color: var(--diff-color) !important;
        }}
        .percent-white {{
            color: #fff !important;
        }}
        </style>
        """
        
        html += f"<h3>{self.get_translation('armor_combinations')}</h3>"
        html += f"<p>{self.get_translation('combinations_explanation')}</p>"
        
        html += '<table class="combo-table"><thead><tr>'
        html += f'<th>{self.get_translation("item")}</th>'
        html += f'<th>{self.get_translation("type")}</th>'
        html += f'<th>{self.get_translation("dispersion")}</th>'
        
        # Add columns for each required resistance
        for resist_type in requirements.keys():
            html += f'<th>{self.get_translation(resist_type)}</th>'
        
        html += '</tr></thead><tbody>'
        
        # Add separator row after header
        html += '<tr class="combo-separator">'
        html += f'<td colspan="{3 + len(requirements)}">&nbsp;</td>'
        html += '</tr>'
        
        # Get dispersion range for color calculation
        all_dispersions = [combo['score']['dispersion'] for combo in combinations]
        min_dispersion = min(all_dispersions) if all_dispersions else 0
        max_dispersion = max(all_dispersions) if all_dispersions else 0
        
        for i, combo in enumerate(combinations, 1):
            # Add separator row between combinations (except before the first one)
            if i > 1:
                html += '<tr class="combo-separator">'
                html += f'<td colspan="{3 + len(requirements)}">&nbsp;</td>'
                html += '</tr>'
            
            # Summary row - combination name with raw scores
            html += '<tr class="combo-summary">'
            
            # Combination name (right-aligned)
            combo_name = f"Combination {i}"
            html += f'<td class="combo-name"><strong>{combo_name}</strong></td>'
            html += f'<td><strong>Total</strong></td>'
            
            # Dispersion with gradient color (lower dispersion = better = greener)
            dispersion = combo['score']['dispersion']
            # Invert the color mapping: lower dispersion should be green (better)
            inverted_dispersion = max_dispersion - dispersion if max_dispersion > min_dispersion else 0
            dispersion_color = self.value_to_color(inverted_dispersion, 0, max_dispersion - min_dispersion)
            html += f'<td class="dispersion-cell" style="background-color: {dispersion_color} !important;">{dispersion:.2f}</td>'
            
            max_value = max(combo['score']['resulting_resistances'][key]['score'] for key in combo['score']['resulting_resistances'])
            min_value = min(combo['score']['resulting_resistances'][key]['score'] for key in combo['score']['resulting_resistances'])
            print(f"Maximum value: {max_value}")
            print(f"Minimum value: {min_value}")

            # Show just the raw scores
            for resist_type in requirements.keys():
                resistance_info = combo['score']['resulting_resistances'].get(resist_type, {'score': 0, 'percentage': 0})
                total_score = resistance_info['score']
                diff_color = self.value_to_color(total_score, min_value, max_value)
                
                html += f'<td class="summary-resist-cell" style="background-color: {diff_color} !important;">{total_score:.0f}</td>'
            
            html += '</tr>'
            
            # Detail rows - one for each armor piece
            for armor in combo['armors']:
                html += '<tr class="combo-detail">'
                
                # Armor name (indented under combination name)
                armor_name = armor.get('Name', 'Unknown')
                html += f'<td class="combo-detail">{armor_name}</td>'
                
                # Armor type
                armor_type = armor.get('Type', 'Unknown')
                html += f'<td class="combo-detail">{armor_type}</td>'
                
                # Empty dispersion cell for detail rows
                html += '<td></td>'
                
                # Individual armor resistance values
                armor_resist_dict = {}
                for resist in armor.get("ResistSheet", []):
                    resist_value = resist.get("ResistValue", 0)
                    
                    armor_resist_dict[resist.get("ResistType")] = resist_value
                
                for resist_type in requirements.keys():
                    value = armor_resist_dict.get(resist_type, 0)
                    
                    html += f'<td class="armor-resist-cell">{value:.0f}</td>'
                
                html += '</tr>'
            
            # Resulting Resistance row - shows percentages with brackets and mean percentage
            html += '<tr class="combo-score-summary">'
            html += f'<td class="combo-detail" style="font-style: italic;">Resulting Resistance</td>'
            html += f'<td class="combo-detail" style="font-style: italic;">Percentages</td>'
            
            # Show mean percentage in the dispersion column
            mean_resistance = combo['score']['mean_resistance']
            html += f'<td class="mean-cell">Mean: {mean_resistance:.2f}%</td>'
            
            # Show percentage with difference in brackets
            for resist_type in requirements.keys():
                resistance_info = combo['score']['resulting_resistances'].get(resist_type, {'score': 0, 'percentage': 0})
                resulting_percentage = resistance_info['percentage']
                required_percentage = requirements[resist_type]
                
                # Calculate difference in percentage points
                difference = resulting_percentage - required_percentage
                
                # Get gradient colors
                diff_color = self.get_difference_color(difference, required_percentage)
                
                # Format difference text
                if difference > 0:
                    diff_text = f"(+{difference:.1f}%)"
                elif difference < 0:
                    diff_text = f"({difference:.1f}%)"
                else:
                    diff_text = "(0%)"
                
                html += f'''<td class="result-resist-cell" style="--diff-color: {diff_color};">
                            <span class="percent-white">{resulting_percentage:.1f}%</span> 
                            <span class="diff-colored">{diff_text}</span>
                            </td>'''
            
            html += '</tr>'
        
        html += '</tbody></table>'
        return html

    def get_difference_color(self, difference: int, required: int) -> str:
        """Get color for difference value based on gradient using existing color system"""
        if required == 0:
            return "#fff"  # White for zero requirement
        
        # Normalize difference as percentage of requirement
        # -1.0 = completely missing requirement, 0 = exact match, +1.0 = double requirement
        normalized_diff = difference / required
        
        # Clamp to reasonable range for color calculation
        normalized_diff = max(-1.0, min(1.0, normalized_diff))
        
        # Map to 0-1 range for color gradient
        # -1.0 -> 0.0 (red), 0.0 -> 0.5 (yellow), +1.0 -> 1.0 (green)
        color_position = (normalized_diff + 1.0) / 2.0
        
        # Use the existing color system from the class
        return self.value_to_color_from_position(color_position)

    def get_coverage_color(self, coverage_pct: float) -> str:
        """Get color for coverage percentage using existing color system"""
        # Map coverage percentage (0-100) to color position (0-1)
        color_position = coverage_pct / 100.0
        return self.value_to_color_from_position(color_position)

    def value_to_color_from_position(self, position: float) -> str:
        """Convert a normalized position (0-1) to color using existing gradient system"""
        # Clamp position to 0-1 range
        position = max(0.0, min(1.0, position))
        
        def hex_to_rgb(hex_color: str) -> tuple:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(r: int, g: int, b: int) -> str:
            return f"#{r:02x}{g:02x}{b:02x}"
        
        # Find the two color stops to interpolate between
        for i in range(len(self.color_stops) - 1):
            pos1, color1 = self.color_stops[i]
            pos2, color2 = self.color_stops[i + 1]
            
            if pos1 <= position <= pos2:
                # Interpolate between these two colors
                local_normalized = (position - pos1) / (pos2 - pos1)
                
                rgb1 = hex_to_rgb(color1)
                rgb2 = hex_to_rgb(color2)
                
                red = int(rgb1[0] + (rgb2[0] - rgb1[0]) * local_normalized)
                green = int(rgb1[1] + (rgb2[1] - rgb1[1]) * local_normalized)
                blue = int(rgb1[2] + (rgb2[2] - rgb1[2]) * local_normalized)
                
                return rgb_to_hex(red, green, blue)
        
        # Fallback to last color if position >= 1
        return self.color_stops[-1][1]

        
    def get_top_armors_per_type(self, filtered_armors: List[Dict], max_per_type: int = 4) -> List[Dict]:
        """Get top armors from each armor type"""
        armor_types = {}
        
        # Group by armor type
        for armor in filtered_armors:
            armor_type = armor.get("Type", "Unknown")
            if armor_type not in armor_types:
                armor_types[armor_type] = []
            armor_types[armor_type].append(armor)
        
        # Get top items from each type (sorted by total resistance)
        result = []
        for armor_type, armors in armor_types.items():
            # Sort by total resistance value (descending)
            sorted_armors = sorted(armors, key=lambda x: sum(
                resist.get("ResistValue", 0) for resist in x.get("ResistSheet", [])
            ), reverse=True)
            
            # Take top N items from this type
            result.extend(sorted_armors[:max_per_type])
        
        return result
    
    def get_resistance_range(self, armors: List[Dict]) -> Dict[str, Tuple[int, int]]:
        """Get min/max values for each resistance type to calculate gradients"""
        ranges = {}
        
        for resist_type in self.resistance_types:
            values = []
            for armor in armors:
                for resist in armor.get("ResistSheet", []):
                    if resist.get("ResistType") == resist_type:
                        values.append(resist.get("ResistValue", 0))
                        break
                else:
                    values.append(0)
            
            if values:
                ranges[resist_type] = (min(values), max(values))
            else:
                ranges[resist_type] = (0, 0)
        
        return ranges
    
    def value_to_color(self, value: int, min_val: int, max_val: int, color_stops: list = None) -> str:
        """Convert resistance value to color gradient with multiple color stops"""
        if max_val == min_val:
            return "#3D3D3D"  # Black for single value
        
        # Default color stops: Red → Yellow → Green
        if self.color_stops is None:
            self.color_stops = [
                (0.0, "#FF0000"),   # Red at 0%
                (0.5, "#FFFF00"),   # Yellow at 50%
                (1.0, "#00FF00")    # Green at 100%
            ]
        
        def hex_to_rgb(hex_color: str) -> tuple:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(r: int, g: int, b: int) -> str:
            return f"#{r:02x}{g:02x}{b:02x}"
        
        # Normalize value between 0 and 1
        normalized = (value - min_val) / (max_val - min_val)
        
        # Find the two color stops to interpolate between
        for i in range(len(self.color_stops) - 1):
            pos1, color1 = self.color_stops[i]
            pos2, color2 = self.color_stops[i + 1]
            
            if pos1 <= normalized <= pos2:
                # Interpolate between these two colors
                local_normalized = (normalized - pos1) / (pos2 - pos1)
                
                rgb1 = hex_to_rgb(color1)
                rgb2 = hex_to_rgb(color2)
                
                red = int(rgb1[0] + (rgb2[0] - rgb1[0]) * local_normalized)
                green = int(rgb1[1] + (rgb2[1] - rgb1[1]) * local_normalized)
                blue = int(rgb1[2] + (rgb2[2] - rgb1[2]) * local_normalized)
                
                return rgb_to_hex(red, green, blue)
        
        # Fallback to last color if normalized > 1
        return color_stops[-1][1]
    
    def create_styled_table_html(self, armors: List[Dict], sort_by: str = "name", sort_order: str = "asc", language: str = None) -> str:
        """Create HTML table with color gradients and sortable headers"""
        if not armors:
            return f"<p>{self.get_translation('no_armors')}</p>"
        
        # Use provided language or fall back to current language
        if language and language != self.current_language:
            self.load_armor_data(language)
        
        # Get resistance ranges for color calculation
        resist_ranges = self.get_resistance_range(armors)
        
        # Define sortable columns and their display names
        sortable_columns = {
            "name": self.get_translation('name'),
            "type": self.get_translation('type'),
            "durability": self.get_translation('durability'),
            "weight": self.get_translation('weight'),
            "blunt": self.get_translation('blunt'),
            "pierce": self.get_translation('pierce'),
            "lacer": self.get_translation('lacer'),
            "fire": self.get_translation('fire'),
            "cold": self.get_translation('cold'),
            "poison": self.get_translation('poison'),
            "shock": self.get_translation('shock'),
            "beam": self.get_translation('beam')
        }
        
        def create_header(column_key, display_name):
            """Create a sortable header cell"""
            if column_key == sort_by:
                # Currently sorted column
                if sort_order == "asc":
                    next_order = "desc"
                    arrow = " ↑"
                else:
                    next_order = "asc"
                    arrow = " ↓"
            else:
                # Not currently sorted
                next_order = "asc"
                arrow = ""
            
            return f'''<th class="sortable-header" data-column="{column_key}" data-next-order="{next_order}" style="cursor: pointer; user-select: none;">{display_name}{arrow}</th>'''
        
        # Start HTML table
        html = f"""
        <style>
        .armor-table {{
            border-collapse: collapse !important;
            width: 100% !important;
            font-family: 'Roboto', Arial, sans-serif !important;
            font-size: 16px !important;
        }}
        .armor-table th, .armor-table td {{
            border: 1px solid #000 !important; /* Force black border */
            padding: 8px !important;
            text-align: left !important; /* Dynamic text alignment */
            background-color: #333 !important; /* Dark grey background */
            color: #fff !important; /* White text for readability */
        }}
        .armor-table th {{
            background-color: #555 !important; /* Slightly darker grey for header */
            font-weight: bold !important;
        }}
        .armor-table th.sortable-header:hover {{
            background-color: #666 !important;
        }}
        .armor-table tr:nth-child(even) td {{
            background-color: #444 !important; /* Alternate row color */
        }}
        .armor-table .resist-cell {{
            font-weight: bold !important;
            color: #000 !important; /* Force black text for resistance cells */
            text-shadow: none !important; /* Remove text shadow for better readability */
            text-align: center !important; /* Keep resistance cells centered for better readability */
        }}
        /* Override Gradio's default table styling */
        .gradio-container .prose table.armor-table,
        .gradio-container .prose table.armor-table tr,
        .gradio-container .prose table.armor-table td,
        .gradio-container .prose table.armor-table th {{
            border: 1px solid #000 !important;
            text-align: left !important;
        }}
        .gradio-container .prose table.armor-table .resist-cell {{
            color: #000 !important;
            text-align: center !important; /* Keep resistance cells centered */
        }}
        </style>
        <table class="armor-table">
        <thead>
        <tr>
        """
        
        # Add headers with translations and sorting functionality
        html += create_header("name", sortable_columns["name"])
        html += create_header("type", sortable_columns["type"])
        html += f"<th>{self.get_translation('description')}</th>"  # Description not sortable
        html += create_header("durability", sortable_columns["durability"])
        html += create_header("weight", sortable_columns["weight"])
        
        # Add resistance headers
        for resist_type in self.resistance_types:
            html += create_header(resist_type, sortable_columns[resist_type])
        
        html += "</tr></thead><tbody>"
        
        # Add armor rows
        for armor in armors:
            html += "<tr>"
            html += f"<td><strong>{armor.get('Name', 'Unknown')}</strong></td>"
            html += f"<td>{armor.get('Type', 'Unknown')}</td>"
            html += f"<td>{armor.get('Description', 'N/A')}</td>"
            html += f"<td>{armor.get('MaxDurability', 'N/A')}</td>"
            html += f"<td>{armor.get('Weight', 'N/A')}</td>"
            
            # Add resistance values with colors
            resist_dict = {}
            for resist in armor.get("ResistSheet", []):
                resist_dict[resist.get("ResistType")] = resist.get("ResistValue", 0)
            
            for resist_type in self.resistance_types:
                value = resist_dict.get(resist_type, 0)
                min_val, max_val = resist_ranges[resist_type]
                color = self.value_to_color(value, min_val, max_val)
                html += f'<td class="resist-cell" style="background-color: {color} !important; color: #000 !important;">{value}</td>'
            
            html += "</tr>"
        
        html += "</tbody></table>"
        
        return html

def create_armor_picker_interface():
    picker = ArmorPicker()
    
    def change_version(version):
        """Handle version change"""
        return picker.change_version(version)
    
    def search_armors(language, version, current_sort_by, current_sort_order, invincible_perk, hardened_talent, hardened_talent_lvl, *args):
        """Search armors with current language"""
        # Ensure version and data are loaded for current language
        picker.change_version(version)
        picker.load_armor_data(language)

        # Parse resistance filter arguments
        resistance_filters = {}
        expected_args = len(picker.resistance_types) * 2
        if len(args) != expected_args:
            args = list(args) + [True, 0] * (expected_args - len(args))
        
        for i, resist_type in enumerate(picker.resistance_types):
            if i * 2 + 1 < len(args):
                enabled = args[i * 2]  # Toggle
                value = args[i * 2 + 1]  # Value
                resistance_filters[resist_type] = {
                    "enabled": enabled,
                    "value": value
                }
            else:
                resistance_filters[resist_type] = {
                    "enabled": True,
                    "value": 0
                }
        
        # Filter armors
        filtered_armors = picker.filter_armors(resistance_filters)

        # Get top 4 from each armor type
        top_armors = picker.get_top_armors_per_type(filtered_armors, max_per_type=99)
        
        # Ensure we have sort parameters
        if not current_sort_by:
            current_sort_by = "name"
            current_sort_order = "asc"
        
        # Sort armors
        sorted_armors = picker.sort_armors(top_armors, current_sort_by, current_sort_order)
        
        # Create styled HTML table with sort indicators - pass language explicitly
        html_table = picker.create_styled_table_html(sorted_armors, current_sort_by, current_sort_order, language)
        
        # Find armor combinations
        combinations_html = picker.find_armor_combinations(resistance_filters, language, invincible_perk, hardened_talent, hardened_talent_lvl)
        
        return html_table, combinations_html, current_sort_by, current_sort_order
    
    def handle_sort_with_js_params(json_data, current_language, current_version, *current_resistance_args):
        """Handle sort with parameters returned from JavaScript as JSON"""
        try:
            import json
            data = json.loads(json_data)
            
            sort_column = data.get('sortColumn', 'name')
            sort_order = data.get('sortOrder', 'asc')
            
            # Use the current Gradio state values instead of JavaScript values
            language = current_language
            version = current_version
            resistance_args = current_resistance_args
            
            # Ensure the picker has the correct language loaded
            picker.change_version(version)
            picker.load_armor_data(language)
            
            if sort_column and sort_order:
                return search_armors(language, version, sort_column, sort_order, *resistance_args)
            else:
                return search_armors(language, version, "name", "asc", *resistance_args)
                    
        except (json.JSONDecodeError, Exception) as e:
            return gr.update(), gr.update(), gr.update()

    
    # Create interface components
    with gr.Blocks(title="QM Armor Picker", theme=gr.themes.Soft()) as interface:
        # Hidden state for sorting
        sort_by_state = gr.State(value="name")
        sort_order_state = gr.State(value="asc")
        
        # Title and language selector on same row
        with gr.Row():
            with gr.Column(scale=4):
                with gr.Row():
                    with gr.Column(scale=3):
                        title_md = gr.Markdown("# QM Armor Picker")
                    with gr.Column(scale=1):
                        # Avatar with decoration and links
                        avatar_html = '''
                        <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%;">
                            <div style="position: relative; display: inline-block; margin-right: 10px;" title="ARZUMATA">
                                <img src="https://avatars.githubusercontent.com/u/54457203?v=4" 
                                     alt="Avatar" 
                                     style="border-radius: 50%; width: 64px; height: 64px;">
                                <img src="https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/50a92b90-66fd-44ed-926a-5f936e7078a1/original=true/user%20avatar%20decoration.gif" 
                                     alt="Avatar Decoration" 
                                     style="position: absolute; top: 0px; scale: 120%">
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <a href="https://github.com/ARZUMATA" target="_blank" style="text-decoration: none; font-size: 18px;">
                                    <svg width="32" height="32" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                                    </svg>
                                </a>
                                <a href="https://civitai.com/user/ARZUMATA" target="_blank" style="text-decoration: none;">
                                    <img src="https://civitai.com/favicon.ico" alt="Civitai" style="width: 32px; height: 32px;">
                                </a>
                                <a href="https://huggingface.co/ARZUMATA" target="_blank" style="text-decoration: none;">
                                    <img src="https://huggingface.co/favicon.ico" alt="Hugging Face" style="width: 32px; height: 32px;">
                                </a>
                            </div>
                        </div>
                        '''
                        gr.HTML(avatar_html)
                
            with gr.Column(scale=1, min_width=150):
                language_selector = gr.Dropdown(
                    choices=list(picker.languages.keys()),
                    value="English",
                    label="Language",
                    scale=0,
                    container=True,
                    elem_classes=["compact-dropdown"]
                )

        # Dynamic content that updates with language
        subtitle_md = gr.Markdown("Select resistance requirements and search for armors. Click column headers to sort results.")
        legend_md = gr.Markdown("**Color Legend**: Resistance values are colored from 🔴 Red (low) to 🟢 Green (high)")
        
        with gr.Row():
            with gr.Column(scale=1):
                filters_md = gr.Markdown("## Resistance Filters")
                
                # Version selector
                with gr.Row():
                    version_selector = gr.Dropdown(
                        choices=["0.9", "0.9.2"],
                        value="0.9",
                        label="Game Version",
                        scale=1
                    )
                
                # Create toggle and value inputs for each resistance type
                resistance_inputs = []
                resistance_checkboxes = []  # Store checkbox references
                
                for resist_type in picker.resistance_types:
                    with gr.Row():
                        toggle = gr.Checkbox(
                            label=f"{resist_type.title()}",
                            value=True,
                        )
                        value = gr.Number(
                            show_label=False,
                            label=None,
                            value=0,
                            minimum=0,
                            maximum=100,
                            step=1
                        )
                        resistance_inputs.extend([toggle, value])
                        resistance_checkboxes.append(toggle)  # Store checkbox reference
                
                with gr.Column(scale=1):
                        invincible_perk = gr.Checkbox(
                            label="Invincible Perk (+12 all resistances)",
                            value=False,
                        )
                        hardened_talent = gr.Checkbox(
                            label="Hardened (+10% resistances)", 
                            value=False,
                            scale=1,
                        )
                        hardened_talent_lvl = gr.Dropdown(
                            choices=[1,2,3,4],
                            value=1,
                            scale=1,
                            label="Hardened Level",
                        )

                search_btn = gr.Button("Search Armors", variant="primary")
            
            with gr.Column(scale=3):
                results_md = gr.Markdown("## Results")
                
                with gr.Tabs():
                    armor_combinations_tab = gr.TabItem("Armor Combinations")
                    with armor_combinations_tab:
                        combination_results = gr.HTML(
                            label="Armor Combinations",
                            value="<p>Click 'Search Armors' to see results...</p>"
                        )
                
                    individual_armors_tab = gr.TabItem("Individual Armors")
                    with individual_armors_tab:
                        individual_results = gr.HTML(
                            label="Matching Armors",
                            value="<p>Click 'Search Armors' to see results...</p>"
                        )
                        
                # Hidden elements for JavaScript communication
                with gr.Column(visible=False):
                    sort_trigger_btn = gr.Button("Sort Trigger", elem_id="sort-trigger-btn")
                    js_data_input = gr.Textbox(elem_id="js-data-input")
        
        # Add JavaScript after interface is loaded
        interface.load(
            fn=None,
            inputs=None,
            outputs=None,
            js="""
            function() {
                window.currentSortColumn = '';
                window.currentSortOrder = '';
                
                function setupTableSortHandlers() {
                    document.removeEventListener('click', handleTableClick);
                    document.addEventListener('click', handleTableClick);
                }
                
                function handleTableClick(event) {
                    const target = event.target;
                    
                    if (target.classList.contains('sortable-header')) {
                        event.preventDefault();
                        
                        const column = target.getAttribute('data-column');
                        const nextOrder = target.getAttribute('data-next-order');
                        
                        if (column && nextOrder) {
                            window.currentSortColumn = column;
                            window.currentSortOrder = nextOrder;
                            
                            const sortButton = document.getElementById('sort-trigger-btn');
                            if (sortButton) {
                                sortButton.click();
                            }
                        }
                    }
                }
                
                setupTableSortHandlers();
                
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'childList') {
                            const armorTable = document.querySelector('.armor-table');
                            if (armorTable) {
                                setupTableSortHandlers();
                            }
                        }
                    });
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                return [];
            }
            """
        )
        
        # Version change handler
        version_selector.change(
            fn=change_version,
            inputs=[version_selector],
            outputs=[individual_results]
        )

        # Language change handler - update text elements and checkbox labels
        def update_ui_language(language):
            picker.load_armor_data(language)
            
            # Update text elements
            updates = []
            updates.append(f"# {picker.get_translation('title')}")  # title
            updates.append(picker.get_translation('subtitle'))  # subtitle
            updates.append(picker.get_translation('color_legend'))  # legend
            updates.append(f"## {picker.get_translation('resistance_filters')}")  # filters
            updates.append(f"## {picker.get_translation('results')}")  # results
            updates.append(picker.get_translation('search_button'))  # search button
            updates.append(f"<p>{picker.get_translation('click_search')}</p>")  # individual_results
            updates.append(f"<p>{picker.get_translation('click_search')}</p>")  # combination_results
            updates.append(gr.Dropdown(label=picker.get_translation('game_version'))) # game version
            updates.append(gr.TabItem(label=picker.get_translation('armor_combinations_tab')))  # armor combinations tab
            updates.append(gr.TabItem(label=picker.get_translation('individual_armors_tab')))  # individual armors tab
            updates.append(gr.Checkbox(label=picker.get_translation('perk_invincible')))
            updates.append(gr.Checkbox(label=picker.get_translation('talent_all_resists')))
            
            # Update checkbox labels for resistance types
            for resist_type in picker.resistance_types:
                updates.append(gr.Checkbox(label=picker.get_translation(resist_type)))
            
            return updates
        
        # Set up event handlers - update text components and checkbox labels
        outputs_list = [title_md, subtitle_md, legend_md, filters_md, results_md, search_btn, individual_results, combination_results, version_selector, armor_combinations_tab, individual_armors_tab, invincible_perk, hardened_talent, hardened_talent_lvl] + resistance_checkboxes

        language_selector.change(
            fn=update_ui_language,
            inputs=[language_selector],
            outputs=outputs_list
        )
        
        # Search button click handler
        def initial_search(language, version, *args):
            result_html, combo_html, new_sort_by, new_sort_order = search_armors(language, version, "name", "asc", *args)
            return result_html, combo_html, new_sort_by, new_sort_order
        
        search_inputs = [language_selector, version_selector, invincible_perk, hardened_talent, hardened_talent_lvl] + resistance_inputs

        search_btn.click(
            fn=initial_search,
            inputs=search_inputs,
            outputs=[individual_results, combination_results, sort_by_state, sort_order_state]
        )
        
        # Sort trigger handler - now uses actual Gradio component values
        sort_inputs = [js_data_input, language_selector, version_selector] + resistance_inputs
        
        # Sort trigger handler
        sort_trigger_btn.click(
            fn=handle_sort_with_js_params,
            inputs=sort_inputs,  # Use actual Gradio components
            outputs=[individual_results, sort_by_state, sort_order_state],
            js="""
            function(dummy_input, language, version, ...resistance_args) {
                // Only send sort parameters from JavaScript, everything else comes from Gradio
                const data = {
                    sortColumn: window.currentSortColumn || 'name',
                    sortOrder: window.currentSortOrder || 'asc'
                };
                
                console.log('Sending sort data:', data);
                console.log('Language from Gradio:', language);
                console.log('Version from Gradio:', version);
                console.log('Resistance args count:', resistance_args.length);
                
                return [JSON.stringify(data), language, version, ...resistance_args];
            }
            """
        )
    
    return interface

demo = create_armor_picker_interface()

# Launch the application
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
    )

