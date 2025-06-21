import gradio as gr
import json
from typing import Dict, List, Any

class ArmorPicker:
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.armor_data = self.load_armor_data()
        self.resistance_types = ["blunt", "pierce", "lacer", "fire", "cold", "poison", "shock", "beam"]
        
    def load_armor_data(self) -> Dict:
        """Load armor data from JSON file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"armors": {"data": []}}
    
    def get_armor_classes(self) -> List[str]:
        """Get unique armor classes from the data"""
        armor_classes = set()
        for armor in self.armor_data.get("armors", {}).get("data", []):
            armor_classes.add(armor.get("ArmorClass", "Unknown"))
        return sorted(list(armor_classes))
    
    def filter_armors(self, resistance_filters: Dict[str, Dict]) -> List[Dict]:
        """Filter armors based on resistance requirements"""
        filtered_armors = []
        
        for armor in self.armor_data.get("armors", {}).get("data", []):
            meets_requirements = True
            
            # Check each resistance requirement
            for resist_type, filter_config in resistance_filters.items():
                if not filter_config["enabled"]:
                    continue
                    
                required_value = filter_config["value"]
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
                filtered_armors.append(armor)
        
        return filtered_armors
    
    def get_top_armors_per_class(self, filtered_armors: List[Dict], max_per_class: int = 4) -> List[Dict]:
        """Get top armors from each armor class"""
        armor_classes = {}
        
        # Group by armor class
        for armor in filtered_armors:
            armor_class = armor.get("ArmorClass", "Unknown")
            if armor_class not in armor_classes:
                armor_classes[armor_class] = []
            armor_classes[armor_class].append(armor)
        
        # Get top items from each class (sorted by total resistance)
        result = []
        for armor_class, armors in armor_classes.items():
            # Sort by total resistance value (descending)
            sorted_armors = sorted(armors, key=lambda x: sum(
                resist.get("ResistValue", 0) for resist in x.get("ResistSheet", [])
            ), reverse=True)
            
            # Take top N items from this class
            result.extend(sorted_armors[:max_per_class])
        
        return result
    
    def format_results(self, armors: List[Dict]) -> str:
        """Format armor results for display"""
        if not armors:
            return "No armors found matching the criteria."
        
        result = f"Found {len(armors)} armor(s):\n\n"
        
        for armor in armors:
            result += f"**{armor.get('Name', 'Unknown')}** ({armor.get('ArmorClass', 'Unknown')})\n"
            result += f"Description: {armor.get('Description', 'N/A')}\n"
            result += f"Durability: {armor.get('MaxDurability', 'N/A')}, Weight: {armor.get('Weight', 'N/A')}\n"
            result += "Resistances:\n"
            
            for resist in armor.get("ResistSheet", []):
                resist_name = resist.get("ResistName", "Unknown")
                resist_value = resist.get("ResistValue", 0)
                result += f"  • {resist_name.title()}: {resist_value}\n"
            
            result += "\n" + "-" * 50 + "\n\n"
        
        return result

def create_armor_picker_interface():
    picker = ArmorPicker("armor_data_english.json")
    
    def search_armors(*args):
        # Parse resistance filter arguments
        resistance_filters = {}
        
        for i, resist_type in enumerate(picker.resistance_types):
            enabled = args[i * 2]  # Toggle
            value = args[i * 2 + 1]  # Value
            resistance_filters[resist_type] = {
                "enabled": enabled,
                "value": value
            }
        
        # Filter armors
        filtered_armors = picker.filter_armors(resistance_filters)
        
        # Get top 4 from each armor class
        top_armors = picker.get_top_armors_per_class(filtered_armors, max_per_class=4)
        
        # Format and return results
        return picker.format_results(top_armors)
    
    # Create interface components
    with gr.Blocks(title="QM Armor Picker", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# QM Armor Picker")
        gr.Markdown("Select resistance requirements and search for armors. Results show up to 4 items from each armor class.")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Resistance Filters")
                
                # Create toggle and value inputs for each resistance type
                inputs = []
                for resist_type in picker.resistance_types:
                    with gr.Row():
                        toggle = gr.Checkbox(
                            label=f"Enable {resist_type.title()}",
                            value=False
                        )
                        value = gr.Number(
                            label=f"Min {resist_type.title()} Value",
                            value=0,
                            minimum=0,
                            maximum=100,
                            step=1
                        )
                        inputs.extend([toggle, value])
                
                search_btn = gr.Button("Search Armors", variant="primary")
            
            with gr.Column(scale=2):
                gr.Markdown("## Results")
                results = gr.Textbox(
                    label="Matching Armors",
                    lines=20,
                    max_lines=30,
                    value="Click 'Search Armors' to see results..."
                )
        
        # Connect search button to function
        search_btn.click(
            fn=search_armors,
            inputs=inputs,
            outputs=results
        )
    
    return interface

if __name__ == "__main__":
    app = create_armor_picker_interface()
    app.launch(share=False)
