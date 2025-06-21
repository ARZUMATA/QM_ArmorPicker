import gradio as gr
import json
import pandas as pd
from typing import Dict, List, Any, Tuple

class ArmorPicker:
    def __init__(self):
        self.resistance_types = ["blunt", "pierce", "lacer", "fire", "cold", "poison", "shock", "beam"]
        self.current_language = "English"
        self.armor_data = {}

        # Language configuration
        self.languages = {
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
        
        # UI translations
        self.translations = {
            "English": {
                "title": "QM Armor Picker",
                "subtitle": "Select resistance requirements and search for armors. Results show up to 4 items from each armor class.",
                "color_legend": "**Color Legend**: Resistance values are colored from 🔴 Red (low) to 🟢 Green (high)",
                "language": "Language",
                "resistance_filters": "Resistance Filters",
                "enable": "Enable",
                "min_value": "Min {} Value",
                "search_button": "Search Armors",
                "results": "Results",
                "click_search": "Click 'Search Armors' to see results...",
                "no_armors": "No armors found matching the criteria.",
                "name": "Name",
                "class": "Class",
                "description": "Description",
                "durability": "Durability",
                "weight": "Weight",
                "blunt": "Blunt",
                "pierce": "Pierce",
                "lacer": "Cut",
                "fire": "Fire",
                "cold": "Cold",
                "poison": "Poison",
                "shock": "Shock",
                "beam": "Beam"
            },
            "Русский": {
                "title": "QM Подборщик Брони",
                "subtitle": "Выберите требования к сопротивлению и найдите броню. Результаты показывают до 4 предметов из каждого класса брони.",
                "color_legend": "**Легенда цветов**: Значения сопротивления окрашены от 🔴 Красного (низкое) до 🟢 Зеленого (высокое)",
                "language": "Язык",
                "resistance_filters": "Фильтры Сопротивления",
                "enable": "Включить",
                "min_value": "Мин. {} Значение",
                "search_button": "Поиск Брони",
                "results": "Результаты",
                "click_search": "Нажмите 'Поиск Брони' для просмотра результатов...",
                "no_armors": "Броня, соответствующая критериям, не найдена.",
                "name": "Название",
                "class": "Класс",
                "description": "Описание",
                "durability": "Прочность",
                "weight": "Вес",
                "blunt": "Дробящий",
                "pierce": "Колющий",
                "lacer": "Режущий",
                "fire": "Огонь",
                "cold": "Холод",
                "poison": "Яд",
                "shock": "Шок",
                "beam": "Луч"
            },
            "Deutsch": {
                "title": "QM Rüstungs-Picker",
                "subtitle": "Wählen Sie Widerstandsanforderungen und suchen Sie nach Rüstungen. Ergebnisse zeigen bis zu 4 Gegenstände aus jeder Rüstungsklasse.",
                "color_legend": "**Farblegende**: Widerstandswerte sind von 🔴 Rot (niedrig) bis 🟢 Grün (hoch) gefärbt",
                "language": "Sprache",
                "resistance_filters": "Widerstandsfilter",
                "enable": "Aktivieren",
                "min_value": "Min. {} Wert",
                "search_button": "Rüstung Suchen",
                "results": "Ergebnisse",
                "click_search": "Klicken Sie auf 'Rüstung Suchen' um Ergebnisse zu sehen...",
                "no_armors": "Keine Rüstung gefunden, die den Kriterien entspricht.",
                "name": "Name",
                "class": "Klasse",
                "description": "Beschreibung",
                "durability": "Haltbarkeit",
                "weight": "Gewicht",
                "blunt": "Stumpf",
                "pierce": "Durchdringend",
                "lacer": "Schneidend",
                "fire": "Feuer",
                "cold": "Kälte",
                "poison": "Gift",
                "shock": "Schock",
                "beam": "Strahl"
            },
            "Français": {
                "title": "QM Sélecteur d'Armure",
                "subtitle": "Sélectionnez les exigences de résistance et recherchez des armures. Les résultats montrent jusqu'à 4 objets de chaque classe d'armure.",
                "color_legend": "**Légende des couleurs**: Les valeurs de résistance sont colorées du 🔴 Rouge (faible) au 🟢 Vert (élevé)",
                "language": "Langue",
                "resistance_filters": "Filtres de Résistance",
                "enable": "Activer",
                "min_value": "Valeur {} Min.",
                "search_button": "Rechercher Armures",
                "results": "Résultats",
                "click_search": "Cliquez sur 'Rechercher Armures' pour voir les résultats...",
                "no_armors": "Aucune armure trouvée correspondant aux critères.",
                "name": "Nom",
                "class": "Classe",
                "description": "Description",
                "durability": "Durabilité",
                "weight": "Poids",
                "blunt": "Contondant",
                "pierce": "Perforant",
                "lacer": "Tranchant",
                "fire": "Feu",
                "cold": "Froid",
                "poison": "Poison",
                "shock": "Choc",
                "beam": "Rayon"
            },
            "Español": {
                "title": "QM Selector de Armadura",
                "subtitle": "Seleccione los requisitos de resistencia y busque armaduras. Los resultados muestran hasta 4 elementos de cada clase de armadura.",
                "color_legend": "**Leyenda de colores**: Los valores de resistencia están coloreados desde 🔴 Rojo (bajo) hasta 🟢 Verde (alto)",
                "language": "Idioma",
                "resistance_filters": "Filtros de Resistencia",
                "enable": "Habilitar",
                "min_value": "Valor {} Mín.",
                "search_button": "Buscar Armaduras",
                "results": "Resultados",
                "click_search": "Haga clic en 'Buscar Armaduras' para ver los resultados...",
                "no_armors": "No se encontraron armaduras que coincidan con los criterios.",
                "name": "Nombre",
                "class": "Clase",
                "description": "Descripción",
                "durability": "Durabilidad",
                "weight": "Peso",
                "blunt": "Contundente",
                "pierce": "Perforante",
                "lacer": "Cortante",
                "fire": "Fuego",
                "cold": "Frío",
                "poison": "Veneno",
                "shock": "Choque",
                "beam": "Rayo"
            },
            "Polski": {
                "title": "QM Wybieracz Zbroi",
                "subtitle": "Wybierz wymagania odporności i wyszukaj zbroje. Wyniki pokazują do 4 przedmiotów z każdej klasy zbroi.",
                "color_legend": "**Legenda kolorów**: Wartości odporności są kolorowane od 🔴 Czerwonego (niskie) do 🟢 Zielonego (wysokie)",
                "language": "Język",
                "resistance_filters": "Filtry Odporności",
                "enable": "Włącz",
                "min_value": "Min. Wartość {}",
                "search_button": "Szukaj Zbroi",
                "results": "Wyniki",
                "click_search": "Kliknij 'Szukaj Zbroi' aby zobaczyć wyniki...",
                "no_armors": "Nie znaleziono zbroi spełniających kryteria.",
                "name": "Nazwa",
                "class": "Klasa",
                "description": "Opis",
                "durability": "Wytrzymałość",
                "weight": "Waga",
                "blunt": "Obuchowe",
                "pierce": "Kłute",
                "lacer": "Cięte",
                "fire": "Ogień",
                "cold": "Zimno",
                "poison": "Trucizna",
                "shock": "Szok",
                "beam": "Promień"
            },
            "Türkçe": {
                "title": "QM Zırh Seçici",
                "subtitle": "Direnç gereksinimlerini seçin ve zırhları arayın. Sonuçlar her zırh sınıfından en fazla 4 öğe gösterir.",
                "color_legend": "**Renk Açıklaması**: Direnç değerleri 🔴 Kırmızı (düşük) ile 🟢 Yeşil (yüksek) arasında renklendirilmiştir",
                "language": "Dil",
                "resistance_filters": "Direnç Filtreleri",
                "enable": "Etkinleştir",
                "min_value": "Min {} Değeri",
                "search_button": "Zırh Ara",
                "results": "Sonuçlar",
                "click_search": "Sonuçları görmek için 'Zırh Ara'ya tıklayın...",
                "no_armors": "Kriterlere uyan zırh bulunamadı.",
                "name": "İsim",
                "class": "Sınıf",
                "description": "Açıklama",
                "durability": "Dayanıklılık",
                "weight": "Ağırlık",
                "blunt": "Künt",
                "pierce": "Delici",
                "lacer": "Kesici",
                "fire": "Ateş",
                "cold": "Soğuk",
                "poison": "Zehir",
                "shock": "Şok",
                "beam": "Işın"
            },
            "Português Brasileiro": {
                "title": "QM Seletor de Armadura",
                "subtitle": "Selecione os requisitos de resistência e procure armaduras. Os resultados mostram até 4 itens de cada classe de armadura.",
                "color_legend": "**Legenda de cores**: Os valores de resistência são coloridos de 🔴 Vermelho (baixo) a 🟢 Verde (alto)",
                "language": "Idioma",
                "resistance_filters": "Filtros de Resistência",
                "enable": "Ativar",
                "min_value": "Valor {} Mín.",
                "search_button": "Buscar Armaduras",
                "results": "Resultados",
                "click_search": "Clique em 'Buscar Armaduras' para ver os resultados...",
                "no_armors": "Nenhuma armadura encontrada que corresponda aos critérios.",
                "name": "Nome",
                "class": "Classe",
                "description": "Descrição",
                "durability": "Durabilidade",
                "weight": "Peso",
                "blunt": "Contundente",
                "pierce": "Perfurante",
                "lacer": "Cortante",
                "fire": "Fogo",
                "cold": "Frio",
                "poison": "Veneno",
                "shock": "Choque",
                "beam": "Raio"
            },
            "한국어": {
                "title": "QM 갑옷 선택기",
                "subtitle": "저항 요구사항을 선택하고 갑옷을 검색하세요. 결과는 각 갑옷 클래스에서 최대 4개 아이템을 보여줍니다.",
                "color_legend": "**색상 범례**: 저항 값은 🔴 빨간색(낮음)에서 🟢 녹색(높음)으로 색칠됩니다",
                "language": "언어",
                "resistance_filters": "저항 필터",
                "enable": "활성화",
                "min_value": "최소 {} 값",
                "search_button": "갑옷 검색",
                "results": "결과",
                "click_search": "결과를 보려면 '갑옷 검색'을 클릭하세요...",
                "no_armors": "기준에 맞는 갑옷을 찾을 수 없습니다.",
                "name": "이름",
                "class": "클래스",
                "description": "설명",
                "durability": "내구도",
                "weight": "무게",
                "blunt": "둔기",
                "pierce": "관통",
                "lacer": "절단",
                "fire": "화염",
                "cold": "냉기",
                "poison": "독",
                "shock": "충격",
                "beam": "광선"
            },
            "日本": {
                "title": "QM アーマーピッカー",
                "subtitle": "抵抗要件を選択して防具を検索します。結果は各防具クラスから最大4つのアイテムを表示します。",
                "color_legend": "**色の凡例**: 抵抗値は🔴赤（低）から🟢緑（高）まで色分けされています",
                "language": "言語",
                "resistance_filters": "抵抗フィルター",
                "enable": "有効化",
                "min_value": "最小{}値",
                "search_button": "防具を検索",
                "results": "結果",
                "click_search": "結果を表示するには「防具を検索」をクリックしてください...",
                "no_armors": "条件に一致する防具が見つかりませんでした。",
                "name": "名前",
                "class": "クラス",
                "description": "説明",
                "durability": "耐久性",
                "weight": "重量",
                "blunt": "打撃",
                "pierce": "貫通",
                "lacer": "切断",
                "fire": "火",
                "cold": "冷気",
                "poison": "毒",
                "shock": "衝撃",
                "beam": "光線"
            },
            "中国人": {
                "title": "QM 护甲选择器",
                "subtitle": "选择抗性要求并搜索护甲。结果显示每个护甲类别最多4个物品。",
                "color_legend": "**颜色图例**: 抗性值从🔴红色（低）到🟢绿色（高）着色",
                "language": "语言",
                "resistance_filters": "抗性过滤器",
                "enable": "启用",
                "min_value": "最小{}值",
                "search_button": "搜索护甲",
                "results": "结果",
                "click_search": '点击"搜索护甲"查看结果...',
                "no_armors": "未找到符合条件的护甲。",
                "name": "名称",
                "class": "类别",
                "description": "描述",
                "durability": "耐久度",
                "weight": "重量",
                "blunt": "钝击",
                "pierce": "穿刺",
                "lacer": "切割",
                "fire": "火焰",
                "cold": "寒冷",
                "poison": "毒素",
                "shock": "冲击",
                "beam": "光束"
            }
        }
        
        # Load default language data
        self.load_armor_data("English")
    
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
    
    def value_to_color(self, value: int, min_val: int, max_val: int) -> str:
        """Convert resistance value to color gradient (red to green)"""
        if max_val == min_val:
            return "#FFFF99"  # Yellow for single value
        
        # Normalize value between 0 and 1
        normalized = (value - min_val) / (max_val - min_val)
        
        # Create gradient from red (0) to green (1)
        red = int(255 * (1 - normalized))
        green = int(255 * normalized)
        blue = 0
        
        return f"#{red:02x}{green:02x}{blue:02x}"
    
    def create_styled_table_html(self, armors: List[Dict]) -> str:
        """Create HTML table with color gradients"""
        if not armors:
            return f"<p>{self.get_translation('no_armors')}</p>"
        
        # Get resistance ranges for color calculation
        resist_ranges = self.get_resistance_range(armors)
        
        # Start HTML table
        html = """
        <style>
        .armor-table {
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
            font-size: 12px;
        }
        .armor-table th, .armor-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        .armor-table th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        .armor-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .resist-cell {
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
        }
        </style>
        <table class="armor-table">
        <thead>
        <tr>
        """
        
        # Add headers with translations
        html += f"<th>{self.get_translation('name')}</th>"
        html += f"<th>{self.get_translation('class')}</th>"
        html += f"<th>{self.get_translation('description')}</th>"
        html += f"<th>{self.get_translation('durability')}</th>"
        html += f"<th>{self.get_translation('weight')}</th>"
        
        # Add resistance headers
        for resist_type in self.resistance_types:
            html += f"<th>{self.get_translation(resist_type)}</th>"
        
        html += "</tr></thead><tbody>"
        
        # Add armor rows
        for armor in armors:
            html += "<tr>"
            html += f"<td><strong>{armor.get('Name', 'Unknown')}</strong></td>"
            html += f"<td>{armor.get('ArmorClass', 'Unknown')}</td>"
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
                html += f'<td class="resist-cell" style="background-color: {color}">{value}</td>'
            
            html += "</tr>"
        
        html += "</tbody></table>"
        
        return html

def create_armor_picker_interface():
    picker = ArmorPicker()
    
    def change_language(language):
        """Handle language change"""
        picker.load_armor_data(language)
        return f"<p>{picker.get_translation('click_search')}</p>"
    
    def search_armors(language, *args):
        """Search armors with current language"""
        # Ensure data is loaded for current language
        picker.load_armor_data(language)
        
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
        
        # Create styled HTML table
        html_table = picker.create_styled_table_html(top_armors)
        
        return html_table
    
    # Create interface components
    with gr.Blocks(title="QM Armor Picker", theme=gr.themes.Soft()) as interface:
        # Language selector
        language_selector = gr.Dropdown(
            choices=list(picker.languages.keys()),
            value="English",
            label="Language / Язык / Sprache / Langue / Idioma / Język / Dil / Idioma / 언어 / 言語 / 语言"
        )
        
        # Dynamic content that updates with language
        title_md = gr.Markdown("# QM Armor Picker")
        subtitle_md = gr.Markdown("Select resistance requirements and search for armors. Results show up to 4 items from each armor class.")
        legend_md = gr.Markdown("**Color Legend**: Resistance values are colored from 🔴 Red (low) to 🟢 Green (high)")
        
        with gr.Row():
            with gr.Column(scale=1):
                filters_md = gr.Markdown("## Resistance Filters")
                
                # Create toggle and value inputs for each resistance type
                inputs = [language_selector]  # Include language selector in inputs
                resistance_inputs = []
                
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
                        resistance_inputs.extend([toggle, value])
                
                inputs.extend(resistance_inputs)
                search_btn = gr.Button("Search Armors", variant="primary")
            
            with gr.Column(scale=3):
                results_md = gr.Markdown("## Results")
                results = gr.HTML(
                    label="Matching Armors",
                    value="<p>Click 'Search Armors' to see results...</p>"
                )
        
        # Language change handler
        def update_ui_language(language):
            picker.load_armor_data(language)
            
            # Update all UI elements with new translations
            updates = []
            updates.append(gr.Markdown.update(value=f"# {picker.get_translation('title')}"))  # title
            updates.append(gr.Markdown.update(value=picker.get_translation('subtitle')))  # subtitle
            updates.append(gr.Markdown.update(value=picker.get_translation('color_legend')))  # legend
            updates.append(gr.Markdown.update(value=f"## {picker.get_translation('resistance_filters')}"))  # filters
            updates.append(gr.Markdown.update(value=f"## {picker.get_translation('results')}"))  # results
            updates.append(gr.Button.update(value=picker.get_translation('search_button')))  # search button
            updates.append(gr.HTML.update(value=f"<p>{picker.get_translation('click_search')}</p>"))  # results
            
            # Update resistance filter labels
            resistance_updates = []
            for i, resist_type in enumerate(picker.resistance_types):
                resistance_updates.append(gr.Checkbox.update(label=f"{picker.get_translation('enable')} {picker.get_translation(resist_type).title()}"))
                resistance_updates.append(gr.Number.update(label=picker.get_translation('min_value').format(picker.get_translation(resist_type).title())))
            
            updates.extend(resistance_updates)
            return updates
        
        # Set up event handlers
        language_selector.change(
            fn=update_ui_language,
            inputs=[language_selector],
            outputs=[title_md, subtitle_md, legend_md, filters_md, results_md, search_btn, results] + resistance_inputs
        )
        
        search_btn.click(
            fn=search_armors,
            inputs=inputs,
            outputs=[results]
        )
    
    return interface

# Launch the application
if __name__ == "__main__":
    app = create_armor_picker_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

