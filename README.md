# QM Armor Picker

Armor selection tool for the Quasimorph game, featuring multi-language support and filtering.

![Preview](media/preview.png)

## Features

### Multi-Language Support
- **11 Languages Available**: English, Russian, German, French, Spanish, Polish, Turkish, Brazilian Portuguese, Korean, Japanese, and Chinese
- Complete UI translation for all supported languages (machine translation used so report any translation issues)

### Game Version Support
- **Version 0.9** and **Version 0.9.2** compatibility
- Easy version switching with automatic data reload
- Version-specific armor statistics

### Advanced Filtering System
- **8 Resistance Types**: Blunt, Pierce, Cut, Fire, Cold, Poison, Shock, and Beam
- Individual enable/disable toggles for each resistance type
- Minimum value thresholds for precise filtering

### Visual Enhancement
- **Color-coded resistance values** with gradient system:
  - 🔴 Red (low resistance)
  - 🟠 Orange (medium-low resistance)
  - 🟡 Yellow (medium resistance)
  - 🟢 Green (high resistance)

### 📊 Armor Information
- Armor name and class
- Descriptions
- Durability and weight
- Complete resistance breakdown

## Installation

### Prerequisites
- Python 3.7+
- Required packages (install via pip):

```bash
pip install gradio
```

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd QM_ArmorPicker
```

2. Ensure armor data files are present in the correct structure:
```
versions/
├── 0.9/
│   ├── armor_data_english.json
│   ├── armor_data_russian.json
│   └── ... (other language files)
└── 0.9.2/
    ├── armor_data_english.json
    ├── armor_data_russian.json
    └── ... (other language files)
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:7860`

## Usage

### Basic Search
1. **Select Language**: Choose your preferred language from the dropdown
2. **Select Game Version**: Pick between version 0.9 or 0.9.2
3. **Set Resistance Filters**: 
   - Toggle on the resistance types you care about
   - Set minimum values for each enabled resistance
4. **Search**: Click "Search Armors" to see results

### Understanding Results
- Results are organized by armor class
- Resistance values are color-coded for easy comparison
- Higher values appear in greener colors, lower values in redder colors


## License

This project is open source and available under the MIT License.

## Author

**ARZUMATA**
- GitHub: [@ARZUMATA](https://github.com/ARZUMATA)
- Civitai: [ARZUMATA](https://civitai.com/user/ARZUMATA)
- Hugging Face: [ARZUMATA](https://huggingface.co/ARZUMATA)

---

*Built with ❤️ for the QM gaming community*
