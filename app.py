import gradio as gr
import json
import pandas as pd
from typing import Dict, List, Any, Tuple

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
        
        # UI translations
        self.translations = {
            "English": {
                "title": "QM Armor Picker",
                "subtitle": "Select resistance requirements and search for armors.",
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
                "beam": "Beam",
                "game_version": "Game Version"
            },
            "Русский": {
                "title": "QM Подборщик Брони",
                "subtitle": "Выберите требования к сопротивлению и найдите броню.",
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
                "pierce": "Проникающий",
                "lacer": "Режущий",
                "fire": "Огонь",
                "cold": "Холод",
                "poison": "Ядовитый",
                "shock": "Электрический",
                "beam": "Лучевой",
                "game_version": "Версия Игры"
            },
            "Deutsch": {
                "title": "QM Rüstungs-Picker",
                "subtitle": "Wählen Sie Widerstandsanforderungen und suchen Sie nach Rüstungen.",
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
                "pierce": "Durchschlag",
                "lacer": "Schneiden",
                "fire": "Feuer",
                "cold": "Kälte",
                "poison": "Gift",
                "shock": "Schock",
                "beam": "Strahl",
                "game_version": "Spielversion"
            },
            "Français": {
                "title": "QM Sélecteur d'Armure",
                "subtitle": "Sélectionnez les exigences de résistance et recherchez des armures.",
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
                "blunt": "Сontondants",
                "pierce": "Perforants",
                "lacer": "Coupe",
                "fire": "Feu",
                "cold": "Froid",
                "poison": "Toxique",
                "shock": "Choc",
                "beam": "Faisceau",
                "game_version": "Version du Jeu"
            },
            "Español": {
                "title": "QM Selector de Armadura",
                "subtitle": "Seleccione los requisitos de resistencia y busque armaduras.",
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
                "blunt": "Daño contundente",
                "pierce": "Perforador",
                "lacer": "Corte",
                "fire": "Fuego",
                "cold": "Frío",
                "poison": "Venenoso",
                "shock": "Choque",
                "beam": "Rayo",
                "game_version": "Versión del Juego"
            },
            "Polski": {
                "title": "QM Wybieracz Zbroi",
                "subtitle": "Wybierz wymagania odporności i wyszukaj zbroje.",
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
                "pierce": "Przebicie",
                "lacer": "Cięcie",
                "fire": "Ogień",
                "cold": "Zimno",
                "poison": "Trujący",
                "shock": "Wstrząs",
                "beam": "Promień",
                "game_version": "Wersja Gry"
            },
            "Türkçe": {
                "title": "QM Zırh Seçici",
                "subtitle": "Direnç gereksinimlerini seçin ve zırhları arayın.",
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
                "blunt": "Darbe",
                "pierce": "Delici",
                "lacer": "Kesik",
                "fire": "Ateş",
                "cold": "Soğuk",
                "poison": "Zehirli",
                "shock": "Şok",
                "beam": "Işın",
                "game_version": "Oyun Sürümü"
            },
            "Português Brasileiro": {
                "title": "QM Seletor de Armadura",
                "subtitle": "Selecione os requisitos de resistência e procure armaduras.",
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
                "blunt": "Golpe",
                "pierce": "Perfuração",
                "lacer": "Corte",
                "fire": "Fogo",
                "cold": "Frio",
                "poison": "Veneno",
                "shock": "Choque",
                "beam": "Feixe",
                "game_version": "Versão do Jogo"
            },
            "한국어": {
                "title": "QM 갑옷 선택기",
                "subtitle": "저항 요구사항을 선택하고 갑옷을 검색하세요.",
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
                "fire": "불",
                "cold": "냉기",
                "poison": "독",
                "shock": "충격",
                "beam": "빔",
                "game_version": "게임 버전"
            },
            "日本": {
                "title": "QM アーマーピッカー",
                "subtitle": "抵抗要件を選択して防具を検索します。",
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
                "pierce": "突き刺し",
                "lacer": "斬撃",
                "fire": "火",
                "cold": "凍結",
                "poison": "毒",
                "shock": "ショック",
                "beam": "ビーム",
                "game_version": "ゲームバージョン"
            },
            "中国人": {
                "title": "QM 护甲选择器",
                "subtitle": "选择抗性要求并搜索护甲。",
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
                "poison": "有毒",
                "shock": "电的",
                "beam": "辐射的",
                "game_version": "游戏版本"
            }
        }
        
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
    
    def search_armors(language, version, current_sort_by, current_sort_order, *args):
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
        
        return html_table, current_sort_by, current_sort_order
    
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
                
                search_btn = gr.Button("Search Armors", variant="primary")
            
            with gr.Column(scale=3):
                results_md = gr.Markdown("## Results")
                results = gr.HTML(
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
            outputs=[results]
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
            updates.append(f"<p>{picker.get_translation('click_search')}</p>")  # results
            updates.append(gr.Dropdown(label=picker.get_translation('game_version'))) # game version

            # Update checkbox labels for resistance types
            for resist_type in picker.resistance_types:
                updates.append(gr.Checkbox(label=picker.get_translation(resist_type)))
            
            return updates
        
        # Set up event handlers - update text components and checkbox labels
        outputs_list = [title_md, subtitle_md, legend_md, filters_md, results_md, search_btn, results, version_selector] + resistance_checkboxes
        
        language_selector.change(
            fn=update_ui_language,
            inputs=[language_selector],
            outputs=outputs_list
        )
        
        # Search button click handler
        def initial_search(language, version, *args):
            result_html, new_sort_by, new_sort_order = search_armors(language, version, "name", "asc", *args)
            return result_html, new_sort_by, new_sort_order
        
        search_inputs = [language_selector, version_selector] + resistance_inputs
        search_btn.click(
            fn=initial_search,
            inputs=search_inputs,
            outputs=[results, sort_by_state, sort_order_state]
        )
        
        # Sort trigger handler - now uses actual Gradio component values
        sort_inputs = [js_data_input, language_selector, version_selector] + resistance_inputs
        
        # Sort trigger handler
        sort_trigger_btn.click(
            fn=handle_sort_with_js_params,
            inputs=sort_inputs,  # Use actual Gradio components
            outputs=[results, sort_by_state, sort_order_state],
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


# Launch the application
if __name__ == "__main__":
    app = create_armor_picker_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

