"""
Configuration constants for MS Batch Generator
"""

# Page configuration
PAGE_CONFIG = {
    "page_title": "MS Batch Generator",
    "page_icon": "⚗️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# File paths
TEMPLATES_FILE = 'saved_templates.json'

# Instrument options
INSTRUMENTS = ['Sciex7500', 'AgilentQQQ', 'HFX-2']

# Plate types per instrument
PLATE_TYPES = {
    'Sciex7500': ['1.5mL VT54 (54 vial)', 'MTP 96'],
    'AgilentQQQ': ['96-well plate'],
    'HFX-2': ['96-well plate']
}

# Sample placement rules
FREQUENCY_RULES = ['At the start only', 'At the end only', 'At fixed interval', 'At start + fixed interval']

# Naming modes
NAMING_MODES = ['None', 'Auto-build (Prefix + Index + Suffix)', 'Enter each name manually', 'Import from CSV/Excel']

# Default sample type configuration
DEFAULT_SAMPLE_TYPES = {
    'standards': {'enabled': False, 'count': 0, 'rule': 'At the start only', 'interval': 1},
    'samples': {'enabled': True, 'count': 0, 'rule': 'At the start only', 'interval': 1},
    'qc': {'enabled': False, 'count': 0, 'rule': 'At fixed interval', 'interval': 10},
    'blanks': {'enabled': False, 'count': 0, 'rule': 'At fixed interval', 'interval': 5}
}

# Navigation steps
STEPS = [
    ('Initial Setup', '1'),
    ('Sample Config', '2'),
    ('Naming Rules', '3'),
    ('Instrument', '4'),
    ('Export', '5')
]

# Sample type mappings for different instruments
AGILENT_SAMPLE_TYPES = ['No injection', 'Blank', 'Sample', 'QC']
AGILENT_INJ_OPTIONS = ['No injection', 'As method']
HFX_SAMPLE_TYPES = ['Blank', 'Unknown', 'QC', 'Std Bracket', 'Std Update', 'Std Clear', 'Start Bracket']

