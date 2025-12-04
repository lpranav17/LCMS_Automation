"""
Instrument Batch/Worklist Generator
A Streamlit application for generating CSV batch files for mass spectrometry instruments.
Refactored for modularity and readability with dark theme and Excel-like editing.
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import re
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

PAGE_CONFIG = {
    "page_title": "MS Batch Generator",
    "page_icon": "⚗️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

TEMPLATES_FILE = 'saved_templates.json'

INSTRUMENTS = ['', 'Sciex7500', 'AgilentQQQ', 'HFX-2']

PLATE_TYPES = {
    'Sciex7500': ['1.5mL VT54 (54 vial)', 'MTP 96'],
    'AgilentQQQ': ['96-well plate'],
    'HFX-2': ['96-well plate']
}

FREQUENCY_RULES = ['At the start only', 'At the end only', 'At fixed interval']

NAMING_MODES = ['None', 'Auto-build (Prefix + Index + Suffix)', 'Enter each name manually', 'Import from CSV/Excel']

DEFAULT_SAMPLE_TYPES = {
    'standards': {'enabled': False, 'count': 0, 'rule': 'At the start only', 'interval': 1},
    'samples': {'enabled': True, 'count': 0, 'rule': 'At the start only', 'interval': 1},
    'qc': {'enabled': False, 'count': 0, 'rule': 'At fixed interval', 'interval': 10},
    'blanks': {'enabled': False, 'count': 0, 'rule': 'At fixed interval', 'interval': 5}
}

STEPS = [
    ('Initial Setup', '1'),
    ('Sample Config', '2'),
    ('Naming Rules', '3'),
    ('Instrument', '4'),
    ('Export', '5')
]


# ============================================================================
# CSS STYLES - DARK THEME
# ============================================================================

def get_dark_theme_css():
    """Return the dark theme CSS styles."""
    return """
    <style>
        /* Import distinctive fonts */
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Root variables for dark theming */
        :root {
            --primary: #22d3ee;
            --primary-dark: #06b6d4;
            --primary-light: #67e8f9;
            --accent: #a78bfa;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
            --surface: #0f172a;
            --surface-elevated: #1e293b;
            --surface-hover: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border: #334155;
            --border-light: #475569;
        }
        
        /* Global styles - Force light text on dark background */
        html, body, [class*="css"] {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #f1f5f9 !important;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        }
        
        /* Force ALL text to be light colored */
        .stApp, .stApp * {
            color: #f1f5f9;
        }
        
        /* Streamlit specific text elements */
        .stMarkdown, .stMarkdown p, .stMarkdown span,
        .stText, .stText p, 
        label, .stSelectbox label, .stTextInput label, .stNumberInput label,
        .stCheckbox label, .stRadio label, .stToggle label,
        [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
        .stExpander summary, .stExpander summary span,
        div[data-testid="stExpander"] summary span,
        .element-container, .element-container p {
            color: #f1f5f9 !important;
        }
        
        /* Sidebar text */
        section[data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }
        
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stTextInput label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {
            color: #f1f5f9 !important;
        }
        
        /* Metric values and labels */
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #f1f5f9 !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #22d3ee !important;
        }
        
        /* Hide default Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom scrollbar - dark */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--surface);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-light);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }
        
        /* Main header with gradient accent */
        .main-header {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
            letter-spacing: -0.025em;
        }
        
        .main-header-accent {
            font-size: 2.25rem;
            font-weight: 700;
            background: linear-gradient(135deg, #22d3ee 0%, #a78bfa 50%, #f472b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1.5rem;
            letter-spacing: -0.03em;
        }
        
        .subtitle {
            font-size: 0.95rem;
            color: var(--text-secondary);
            margin-bottom: 2rem;
            font-weight: 400;
        }
        
        /* Section cards - dark */
        .section-card {
            background: var(--surface-elevated);
            border-radius: 16px;
            padding: 1.75rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), 0 0 40px rgba(34, 211, 238, 0.05);
            transition: all 0.3s ease;
        }
        
        .section-card:hover {
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4), 0 0 60px rgba(34, 211, 238, 0.1);
            border-color: var(--border-light);
        }
        
        /* Section headers */
        .section-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1.25rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--border);
        }
        
        .section-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
        }
        
        .icon-blue { background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%); }
        .icon-green { background: linear-gradient(135deg, #10b981 0%, #34d399 100%); }
        .icon-amber { background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%); }
        .icon-purple { background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%); }
        .icon-cyan { background: linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%); }
        
        /* Progress stepper - dark */
        .stepper-container {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            padding: 1rem 0;
        }
        
        .step-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.625rem 0.875rem;
            border-radius: 10px;
            transition: all 0.2s ease;
            font-size: 0.875rem;
        }
        
        .step-item.completed {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(52, 211, 153, 0.1) 100%);
            color: #34d399;
        }
        
        .step-item.active {
            background: linear-gradient(135deg, rgba(34, 211, 238, 0.2) 0%, rgba(167, 139, 250, 0.1) 100%);
            color: #22d3ee;
            font-weight: 600;
        }
        
        .step-item.pending {
            color: var(--text-muted);
        }
        
        .step-number {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .step-item.completed .step-number {
            background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
            color: white;
        }
        
        .step-item.active .step-number {
            background: linear-gradient(135deg, #22d3ee 0%, #a78bfa 100%);
            color: white;
        }
        
        .step-item.pending .step-number {
            background: var(--border);
            color: var(--text-muted);
        }
        
        /* Alert boxes - dark */
        .alert {
            padding: 1rem 1.25rem;
            border-radius: 12px;
            margin: 1rem 0;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            font-size: 0.9rem;
            line-height: 1.5;
        }
        
        .alert-icon {
            font-size: 1.1rem;
            flex-shrink: 0;
            margin-top: 0.1rem;
        }
        
        .alert-warning {
            background: rgba(251, 191, 36, 0.15);
            border: 1px solid rgba(251, 191, 36, 0.3);
            color: #fbbf24;
        }
        
        .alert-info {
            background: rgba(34, 211, 238, 0.15);
            border: 1px solid rgba(34, 211, 238, 0.3);
            color: #22d3ee;
        }
        
        .alert-success {
            background: rgba(52, 211, 153, 0.15);
            border: 1px solid rgba(52, 211, 153, 0.3);
            color: #34d399;
        }
        
        .alert-error {
            background: rgba(248, 113, 113, 0.15);
            border: 1px solid rgba(248, 113, 113, 0.3);
            color: #f87171;
        }
        
        /* Metric cards - dark */
        .metric-card {
            background: var(--surface-elevated);
            border-radius: 12px;
            padding: 1.25rem;
            border: 1px solid var(--border);
            text-align: center;
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            border-color: var(--primary);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            font-family: 'JetBrains Mono', monospace;
            line-height: 1.2;
        }
        
        .metric-label {
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.25rem;
            font-weight: 500;
        }
        
        /* Buttons - dark */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.9rem;
            padding: 0.625rem 1.25rem;
            transition: all 0.2s ease;
            border: 1px solid var(--border);
            background: var(--surface-elevated);
            color: var(--text-primary);
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            border-color: var(--primary);
            background: var(--surface-hover);
        }
        
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #22d3ee 0%, #a78bfa 100%);
            color: #0f172a;
            border: none;
        }
        
        .stDownloadButton > button {
            background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
            color: #0f172a;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            transition: all 0.2s ease;
        }
        
        .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 20px rgba(52, 211, 153, 0.4);
        }
        
        /* Input fields - dark */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div,
        .stSelectbox > div > div > div {
            border-radius: 10px;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            background-color: #0f172a !important;
            color: #f1f5f9 !important;
            font-family: 'DM Sans', sans-serif;
        }
        
        /* Selectbox dropdown text */
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [data-baseweb="select"] div,
        [data-baseweb="select"] .css-1dimb5e-singleValue,
        [data-baseweb="select"] input {
            color: #f1f5f9 !important;
        }
        
        /* Dropdown menu */
        [data-baseweb="popover"], [data-baseweb="menu"],
        [data-baseweb="popover"] li, [data-baseweb="menu"] li {
            background-color: #1e293b !important;
            color: #f1f5f9 !important;
        }
        
        [data-baseweb="popover"] li:hover, [data-baseweb="menu"] li:hover {
            background-color: #334155 !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.2) !important;
        }
        
        /* Input placeholder */
        .stTextInput input::placeholder,
        .stNumberInput input::placeholder {
            color: #64748b !important;
        }
        
        /* Expander styling - dark */
        div[data-testid="stExpander"] {
            background: #0f172a !important;
            background-color: #0f172a !important;
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }
        
        div[data-testid="stExpander"] > div:first-child {
            padding: 0.75rem 1rem;
            background: #0f172a !important;
        }
        
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary span,
        div[data-testid="stExpander"] p,
        div[data-testid="stExpander"] label {
            color: #f1f5f9 !important;
        }
        
        /* Sidebar - dark */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
            border-right: 1px solid var(--border);
        }
        
        section[data-testid="stSidebar"] > div {
            padding-top: 1.5rem;
            background: transparent !important;
        }
        
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4 {
            color: #f1f5f9 !important;
        }
        
        /* Sidebar header */
        .sidebar-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.5rem 0 1rem 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1rem;
        }
        
        .sidebar-logo {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #22d3ee 0%, #a78bfa 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }
        
        .sidebar-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.2;
        }
        
        .sidebar-subtitle {
            font-size: 0.75rem;
            color: var(--text-muted);
            font-weight: 500;
        }
        
        /* Template section */
        .template-section {
            background: var(--surface);
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
        }
        
        .template-title {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
        }
        
        /* Code blocks - dark */
        .code-preview {
            background: #0f172a;
            color: #22d3ee;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            margin-top: 0.5rem;
            border: 1px solid var(--border);
        }
        
        /* Footer - dark */
        .footer {
            text-align: center;
            padding: 2rem 0 1rem 0;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
            margin-top: 2rem;
        }
        
        .footer a {
            color: var(--primary);
            text-decoration: none;
        }
        
        /* Instrument badges - dark */
        .instrument-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .badge-sciex { background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
        .badge-agilent { background: rgba(34, 211, 238, 0.2); color: #22d3ee; border: 1px solid rgba(34, 211, 238, 0.3); }
        .badge-hfx { background: rgba(167, 139, 250, 0.2); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.3); }
        
        /* Toggle styling - dark */
        .stToggle > label > div,
        .stToggle label,
        .stToggle span,
        .stCheckbox label,
        .stCheckbox span,
        .stRadio label,
        .stRadio span {
            color: #f1f5f9 !important;
        }
        
        /* Number input */
        .stNumberInput label,
        .stNumberInput [data-testid="stWidgetLabel"] {
            color: #f1f5f9 !important;
        }
        
        /* File uploader */
        .stFileUploader label,
        .stFileUploader span,
        [data-testid="stFileUploader"] label {
            color: #f1f5f9 !important;
        }
        
        [data-testid="stFileUploader"] section {
            background-color: #1e293b !important;
            border-color: #334155 !important;
        }
        
        /* Multiselect */
        .stMultiSelect label,
        .stMultiSelect [data-testid="stWidgetLabel"] {
            color: #f1f5f9 !important;
        }
        
        [data-baseweb="tag"] {
            background-color: #334155 !important;
            color: #f1f5f9 !important;
        }
        
        /* Data editor / dataframe */
        .stDataFrame, [data-testid="stDataFrame"] {
            background-color: #1e293b !important;
        }
        
        /* Help tooltip */
        .stTooltipIcon {
            color: #64748b !important;
        }
        
        /* AG-Grid dark theme customization */
        .ag-theme-alpine-dark {
            --ag-background-color: #1e293b;
            --ag-header-background-color: #0f172a;
            --ag-odd-row-background-color: #1e293b;
            --ag-row-hover-color: #334155;
            --ag-border-color: #334155;
            --ag-header-foreground-color: #f1f5f9;
            --ag-foreground-color: #f1f5f9;
            --ag-secondary-foreground-color: #94a3b8;
            --ag-range-selection-border-color: #22d3ee;
            --ag-range-selection-background-color: rgba(34, 211, 238, 0.2);
        }
        
        /* Excel-like grid container */
        .grid-container {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
        }
        
        .grid-toolbar {
            display: flex;
            gap: 0.5rem;
            padding: 0.75rem;
            background: var(--surface);
            border-bottom: 1px solid var(--border);
        }
        
        .grid-toolbar-btn {
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .main-header-accent {
                font-size: 1.5rem;
            }
            .section-card {
                padding: 1.25rem;
            }
        }
    </style>
    """


# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def init_session_state():
    """Initialize all session state variables with defaults."""
    defaults = {
        'step': 1,
        'instrument': None,
        'project_name': '',
        'parent_folder': '',
        'sample_types': DEFAULT_SAMPLE_TYPES.copy(),
        'naming_mode': 'None',
        'naming_config': {},
        'sequence_df': None,
        'templates': {},
        'ms_method': '',
        'lc_method': '',
        'plate_type': '1.5mL VT54 (54 vial)',
        'plate_number': 1,
        'injection_volume': 1.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            if isinstance(value, dict):
                st.session_state[key] = value.copy()
            else:
                st.session_state[key] = value


def reset_session_state():
    """Reset all session state to defaults."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


# ============================================================================
# TEMPLATE MANAGEMENT
# ============================================================================

def load_templates():
    """Load saved templates from JSON file."""
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_template(name, config):
    """Save a configuration template."""
    templates = load_templates()
    templates[name] = config
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=2)


def delete_template(name):
    """Delete a saved template."""
    templates = load_templates()
    if name in templates:
        del templates[name]
        with open(TEMPLATES_FILE, 'w') as f:
            json.dump(templates, f, indent=2)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_project_name(name):
    """Validate project name format (e.g., MPG_25-12_GaIEMA)."""
    pattern = r'^[A-Za-z]{2,3}_\d{2}-\d{2}_\w+$'
    return bool(re.match(pattern, name)) if name else False


def generate_sequence(sample_types):
    """Generate the sample sequence based on frequency rules."""
    sequence = []
    
    standards = sample_types.get('standards', {})
    samples = sample_types.get('samples', {})
    qc = sample_types.get('qc', {})
    blanks = sample_types.get('blanks', {})
    
    # Start-only items
    for stype, config in [('Standard', standards), ('Blank', blanks), ('QC', qc)]:
        if config.get('enabled') and config.get('rule') == 'At the start only':
            for i in range(config.get('count', 0)):
                sequence.append({'type': stype, 'index': i + 1})
    
    # Build main sequence with samples
    if samples.get('enabled'):
        sample_count = samples.get('count', 0)
        blank_interval = blanks.get('interval', 0) if blanks.get('enabled') and blanks.get('rule') == 'At fixed interval' else 0
        qc_interval = qc.get('interval', 0) if qc.get('enabled') and qc.get('rule') == 'At fixed interval' else 0
        
        blank_counter = 0
        qc_counter = 0
        blank_placed = 0
        qc_placed = 0
        
        for i in range(1, sample_count + 1):
            if blank_interval > 0 and i > 1 and (i - 1) % blank_interval == 0:
                if blanks.get('enabled') and blank_placed < blanks.get('count', 0):
                    blank_counter += 1
                    blank_placed += 1
                    sequence.append({'type': 'Blank', 'index': blank_counter})
            
            if qc_interval > 0 and i > 1 and (i - 1) % qc_interval == 0:
                if qc.get('enabled') and qc_placed < qc.get('count', 0):
                    qc_counter += 1
                    qc_placed += 1
                    sequence.append({'type': 'QC', 'index': qc_counter})
            
            sequence.append({'type': 'Sample', 'index': i})
    
    # End-only items
    for stype, config in [('Standard', standards), ('Blank', blanks), ('QC', qc)]:
        if config.get('enabled') and config.get('rule') == 'At the end only':
            for i in range(config.get('count', 0)):
                sequence.append({'type': stype, 'index': i + 1})
    
    return sequence


def generate_sample_name(item, naming_mode, sequence=None):
    """Generate a sample name based on the naming mode."""
    type_name = item['type'].lower()
    idx = item['index']
    
    if naming_mode == 'None':
        return f"{item['type']}{idx}"
    elif naming_mode == 'Auto-build (Prefix + Index + Suffix)':
        prefix = st.session_state.get(f"prefix_{type_name}", type_name[:3].upper())
        suffix = st.session_state.get(f"suffix_{type_name}", "")
        index_start = st.session_state.get(f"index_start_{type_name}", 1)
        
        if suffix:
            return f"{prefix}_{index_start + idx - 1}_{suffix}"
        return f"{prefix}_{index_start + idx - 1}"
    elif naming_mode == 'Import from CSV/Excel' and hasattr(st.session_state, 'imported_names'):
        names = st.session_state.imported_names
        if sequence:
            total_idx = sum(1 for s in sequence[:sequence.index(item)] if s['type'] == item['type'])
            if total_idx < len(names):
                return names[total_idx]
    
    return f"{item['type']}{idx}"


# ============================================================================
# AG-GRID CONFIGURATION
# ============================================================================

def configure_aggrid(df, instrument):
    """Configure AG-Grid with Excel-like features."""
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Enable Excel-like features
    gb.configure_default_column(
        editable=True,
        resizable=True,
        sortable=True,
        filter=True,
        wrapText=True,
        autoHeight=True
    )
    
    # Enable row drag and drop
    gb.configure_grid_options(
        rowDragManaged=True,
        rowDragEntireRow=True,
        animateRows=True,
        enableRangeSelection=True,
        suppressRowClickSelection=True,
        rowSelection='multiple',
        enableCellTextSelection=True,
        copyHeadersToClipboard=True
    )
    
    # First column with drag handle
    first_col = df.columns[0]
    gb.configure_column(first_col, rowDrag=True, rowDragText=None)
    
    # Configure specific columns based on instrument
    if instrument == 'Sciex7500':
        if 'Vial Position' in df.columns:
            gb.configure_column('Vial Position', type=['numericColumn'], editable=True)
        if 'Injection Volume' in df.columns:
            gb.configure_column('Injection Volume', type=['numericColumn'], valueFormatter="value.toFixed(2)")
    
    elif instrument == 'AgilentQQQ':
        if 'Sample Type' in df.columns:
            gb.configure_column('Sample Type', 
                cellEditor='agSelectCellEditor',
                cellEditorParams={'values': ['No injection', 'Blank', 'Sample', 'QC']}
            )
        if 'Injection Volume' in df.columns:
            gb.configure_column('Injection Volume',
                cellEditor='agSelectCellEditor',
                cellEditorParams={'values': ['No injection', 'As method']}
            )
    
    elif instrument == 'HFX-2':
        if 'Sample Type' in df.columns:
            gb.configure_column('Sample Type',
                cellEditor='agSelectCellEditor',
                cellEditorParams={'values': ['Blank', 'Unknown', 'QC', 'Std Bracket', 'Std Update', 'Std Clear', 'Start Bracket']}
            )
        if 'Inj Vol' in df.columns:
            gb.configure_column('Inj Vol', type=['numericColumn'], valueFormatter="value.toFixed(2)")
        if 'Level' in df.columns:
            gb.configure_column('Level', type=['numericColumn'])
    
    # Enable pagination for large datasets
    if len(df) > 50:
        gb.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=25)
    
    return gb.build()


def render_aggrid(df, instrument, key):
    """Render the AG-Grid with Excel-like editing capabilities."""
    grid_options = configure_aggrid(df, instrument)
    
    st.markdown("""
        <div class="alert alert-info" style="margin-bottom: 1rem;">
            <span class="alert-icon">💡</span>
            <span><strong>Excel-like editing:</strong> Drag rows to reorder • Double-click to edit • Ctrl+C/V to copy/paste • Click headers to sort</span>
        </div>
    """, unsafe_allow_html=True)
    
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=True,
        theme='alpine-dark',
        height=400,
        allow_unsafe_jscode=True,
        key=key
    )
    
    return grid_response['data']


# ============================================================================
# UI COMPONENTS - SIDEBAR
# ============================================================================

def render_sidebar():
    """Render the sidebar with navigation and template management."""
    with st.sidebar:
        # Sidebar header
        st.markdown("""
            <div class="sidebar-header">
                <div class="sidebar-logo">⚗️</div>
                <div>
                    <div class="sidebar-title">MS Batch Gen</div>
                    <div class="sidebar-subtitle">Worklist Generator</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Progress stepper
        render_progress_stepper()
        
        st.markdown("---")
        
        # Template Management
        render_template_management()
        
        st.markdown("---")
        
        # Reset button
        if st.button("🗑️ Reset All", use_container_width=True, type="secondary"):
            reset_session_state()
            st.rerun()


def render_progress_stepper():
    """Render the step progress indicator."""
    current_step = st.session_state.step
    
    st.markdown('<div class="stepper-container">', unsafe_allow_html=True)
    for i, (step_name, step_num) in enumerate(STEPS, 1):
        if i < current_step:
            status = "completed"
            icon = "✓"
        elif i == current_step:
            status = "active"
            icon = step_num
        else:
            status = "pending"
            icon = step_num
        
        st.markdown(f"""
            <div class="step-item {status}">
                <div class="step-number">{icon}</div>
                <span>{step_name}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_template_management():
    """Render template save/load functionality."""
    st.markdown('<div class="template-title">📁 Saved Templates</div>', unsafe_allow_html=True)
    
    templates = load_templates()
    
    if templates:
        selected_template = st.selectbox(
            "Select Template",
            options=[''] + list(templates.keys()),
            key='template_select',
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load", disabled=not selected_template, use_container_width=True):
                if selected_template:
                    config = templates[selected_template]
                    st.session_state.sample_types = config.get('sample_types', DEFAULT_SAMPLE_TYPES.copy())
                    st.session_state.naming_mode = config.get('naming_mode', 'None')
                    st.rerun()
        with col2:
            if st.button("Delete", disabled=not selected_template, use_container_width=True):
                if selected_template:
                    delete_template(selected_template)
                    st.rerun()
    else:
        st.markdown("""
            <div style="color: var(--text-muted); font-size: 0.85rem; padding: 0.5rem 0;">
                No templates saved yet
            </div>
        """, unsafe_allow_html=True)
    
    # Save new template
    with st.expander("💾 Save New Template"):
        template_name = st.text_input("Template Name", key='new_template_name', placeholder="My Template")
        if st.button("Save Template", disabled=not template_name, use_container_width=True):
            config = {
                'sample_types': st.session_state.sample_types,
                'naming_mode': st.session_state.naming_mode,
            }
            save_template(template_name, config)
            st.success(f"✓ Saved '{template_name}'")
            st.rerun()


# ============================================================================
# UI COMPONENTS - STEPS
# ============================================================================

def render_step1_initial_setup():
    """Render Step 1: Initial Setup."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-blue">📋</div>
            <span>Step 1: Initial Setup</span>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        instrument = st.selectbox(
            "Select Instrument",
            options=INSTRUMENTS,
            index=INSTRUMENTS.index(st.session_state.instrument) if st.session_state.instrument else 0,
            help="Choose the mass spectrometry instrument"
        )
        st.session_state.instrument = instrument if instrument else None
        
        project_name = st.text_input(
            "Project Name",
            value=st.session_state.project_name,
            placeholder="e.g., MPG_25-12_GaIEMA",
            help="Format: 2-3 letter initials_YY-MM_ProjectCode"
        )
        st.session_state.project_name = project_name
        
        if project_name and not validate_project_name(project_name):
            st.markdown("""
                <div class="alert alert-warning">
                    <span class="alert-icon">⚠️</span>
                    <span>Project name doesn't match recommended format (e.g., MPG_25-12_GaIEMA)</span>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        parent_folder = st.text_input(
            "Data Folder Path",
            value=st.session_state.parent_folder,
            placeholder="D:\\Data\\Project_Folder",
            help="Path where all data files will be saved"
        )
        st.session_state.parent_folder = parent_folder
        
        if parent_folder:
            if st.session_state.instrument == 'AgilentQQQ' and not parent_folder.upper().startswith('D:'):
                st.markdown("""
                    <div class="alert alert-warning">
                        <span class="alert-icon">⚠️</span>
                        <span>AgilentQQQ requires folder path on D: drive</span>
                    </div>
                """, unsafe_allow_html=True)
    
    # Navigation
    if st.session_state.instrument and project_name:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continue to Sample Configuration →", key='next_1', type="primary"):
            st.session_state.step = max(st.session_state.step, 2)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_step2_sample_config():
    """Render Step 2: Sample Types Configuration."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-green">🧫</div>
            <span>Step 2: Sample Types & Frequency Rules</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Sample type toggles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.session_state.sample_types['standards']['enabled'] = st.toggle(
            "📊 Standards",
            value=st.session_state.sample_types['standards']['enabled']
        )
    with col2:
        st.session_state.sample_types['samples']['enabled'] = st.toggle(
            "🧪 Samples",
            value=st.session_state.sample_types['samples']['enabled']
        )
    with col3:
        st.session_state.sample_types['qc']['enabled'] = st.toggle(
            "✓ Quality Controls",
            value=st.session_state.sample_types['qc']['enabled']
        )
    with col4:
        st.session_state.sample_types['blanks']['enabled'] = st.toggle(
            "○ Blanks",
            value=st.session_state.sample_types['blanks']['enabled']
        )
    
    # Warning if no QC or blanks
    if not st.session_state.sample_types['qc']['enabled'] and not st.session_state.sample_types['blanks']['enabled']:
        st.markdown("""
            <div class="alert alert-warning">
                <span class="alert-icon">💡</span>
                <span><strong>Recommendation:</strong> Consider adding QC or Blank samples for quality assurance.</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Configuration for active sample types
    active_types = [(name, config) for name, config in st.session_state.sample_types.items() if config['enabled']]
    
    if active_types:
        for type_name, config in active_types:
            with st.expander(f"⚙️ Configure {type_name.title()}", expanded=True):
                cols = st.columns([2, 2, 2])
                
                with cols[0]:
                    count = st.number_input(
                        f"Number of {type_name}",
                        min_value=0,
                        max_value=500,
                        value=config['count'],
                        key=f"count_{type_name}"
                    )
                    st.session_state.sample_types[type_name]['count'] = count
                
                with cols[1]:
                    if type_name != 'samples':
                        rule = st.selectbox(
                            f"Placement Rule",
                            options=FREQUENCY_RULES,
                            index=FREQUENCY_RULES.index(config['rule']) if config['rule'] in FREQUENCY_RULES else 0,
                            key=f"rule_{type_name}"
                        )
                        st.session_state.sample_types[type_name]['rule'] = rule
                    else:
                        st.markdown("""
                            <div class="alert alert-info" style="margin: 0; padding: 0.75rem;">
                                <span>Samples form the main sequence</span>
                            </div>
                        """, unsafe_allow_html=True)
                
                with cols[2]:
                    if type_name != 'samples' and st.session_state.sample_types[type_name].get('rule') == 'At fixed interval':
                        interval = st.number_input(
                            f"Insert every N samples",
                            min_value=1,
                            max_value=100,
                            value=config.get('interval', 5),
                            key=f"interval_{type_name}"
                        )
                        st.session_state.sample_types[type_name]['interval'] = interval
    
    # Preview sequence summary
    if any(config['enabled'] and config['count'] > 0 for config in st.session_state.sample_types.values()):
        sequence = generate_sequence(st.session_state.sample_types)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Sequence Summary")
        
        summary = {}
        for item in sequence:
            summary[item['type']] = summary.get(item['type'], 0) + 1
        
        cols = st.columns(len(summary) + 1)
        with cols[0]:
            st.metric("Total Injections", len(sequence))
        for i, (stype, count) in enumerate(summary.items(), 1):
            with cols[i]:
                st.metric(stype, count)
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key='back_2'):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if any(config['enabled'] and config['count'] > 0 for config in st.session_state.sample_types.values()):
            if st.button("Continue to Naming →", key='next_2', type="primary"):
                st.session_state.step = max(st.session_state.step, 3)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_step3_naming_rules():
    """Render Step 3: Sample Naming Rules."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-amber">✏️</div>
            <span>Step 3: Sample Naming Rules</span>
        </div>
    """, unsafe_allow_html=True)
    
    naming_mode = st.selectbox(
        "Naming Mode",
        options=NAMING_MODES,
        index=NAMING_MODES.index(st.session_state.naming_mode) if st.session_state.naming_mode in NAMING_MODES else 0
    )
    st.session_state.naming_mode = naming_mode
    
    if naming_mode == 'Auto-build (Prefix + Index + Suffix)':
        st.markdown("""
            <div class="alert alert-info">
                <span class="alert-icon">💡</span>
                <span>Names are generated as <code style="background: rgba(255,255,255,0.1); padding: 0.2rem 0.4rem; border-radius: 4px;">Prefix_Index_Suffix</code> (e.g., Matrix_1_dil)</span>
            </div>
        """, unsafe_allow_html=True)
        
        col_order = st.multiselect(
            "Name Component Order",
            options=['Prefix', 'Index', 'Suffix'],
            default=['Prefix', 'Index', 'Suffix'],
            help="Reorder how name parts are combined"
        )
        
        for type_name, config in st.session_state.sample_types.items():
            if config['enabled'] and config['count'] > 0:
                with st.expander(f"🏷️ {type_name.title()} Naming", expanded=True):
                    cols = st.columns(3)
                    
                    with cols[0]:
                        prefix = st.text_input(
                            "Prefix",
                            value=type_name[:3].upper() if type_name != 'samples' else 'SPL',
                            key=f"prefix_{type_name}"
                        )
                    
                    with cols[1]:
                        index_start = st.number_input(
                            "Start Index",
                            min_value=1,
                            value=1,
                            key=f"index_start_{type_name}"
                        )
                    
                    with cols[2]:
                        suffix = st.text_input(
                            "Suffix (optional)",
                            value="",
                            key=f"suffix_{type_name}",
                            placeholder="e.g., uM, dil"
                        )
                    
                    if prefix:
                        parts = {'Prefix': prefix, 'Index': str(index_start), 'Suffix': suffix}
                        sample_name = '_'.join([parts[c] for c in col_order if parts.get(c)])
                        st.markdown(f'<div class="code-preview">Preview: {sample_name}</div>', unsafe_allow_html=True)
    
    elif naming_mode == 'Import from CSV/Excel':
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file with sample names",
            type=['csv', 'xlsx'],
            help="File should have a column with sample names"
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("**Preview of uploaded file:**")
                st.dataframe(df.head(), use_container_width=True)
                
                name_column = st.selectbox(
                    "Select column containing sample names",
                    options=df.columns.tolist()
                )
                
                if name_column:
                    st.session_state.imported_names = df[name_column].tolist()
                    st.markdown(f"""
                        <div class="alert alert-success">
                            <span class="alert-icon">✓</span>
                            <span>Successfully imported {len(st.session_state.imported_names)} sample names</span>
                        </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                    <div class="alert alert-error">
                        <span class="alert-icon">✕</span>
                        <span>Error reading file: {e}</span>
                    </div>
                """, unsafe_allow_html=True)
    
    elif naming_mode == 'None':
        st.markdown("""
            <div class="alert alert-info">
                <span class="alert-icon">📝</span>
                <span>Samples will be automatically numbered: Sample1, Sample2, QC1, Blank1, etc.</span>
            </div>
        """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key='back_3'):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Continue to Instrument Config →", key='next_3', type="primary"):
            st.session_state.step = max(st.session_state.step, 4)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_step4_instrument_config():
    """Render Step 4: Instrument-Specific Configuration with AG-Grid."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    badge_class = {
        'Sciex7500': 'badge-sciex',
        'AgilentQQQ': 'badge-agilent',
        'HFX-2': 'badge-hfx'
    }.get(st.session_state.instrument, 'badge-sciex')
    
    st.markdown(f"""
        <div class="section-header">
            <div class="section-icon icon-purple">⚙️</div>
            <span>Step 4: Instrument Configuration</span>
        </div>
        <div class="instrument-badge {badge_class}">
            🔬 {st.session_state.instrument}
        </div>
    """, unsafe_allow_html=True)
    
    sequence = generate_sequence(st.session_state.sample_types)
    
    # Instrument-specific configuration
    if st.session_state.instrument == 'Sciex7500':
        df = render_sciex7500_config(sequence)
    elif st.session_state.instrument == 'AgilentQQQ':
        df = render_agilent_config(sequence)
    elif st.session_state.instrument == 'HFX-2':
        df = render_hfx2_config(sequence)
    else:
        df = None
    
    # Validation warnings
    if df is not None:
        validate_positions(df)
    
    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key='back_4'):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Continue to Export →", key='next_4', type="primary"):
            st.session_state.step = max(st.session_state.step, 5)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_sciex7500_config(sequence):
    """Render Sciex7500 configuration and return DataFrame."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input(
            "MS Method Path",
            value=st.session_state.ms_method,
            placeholder="D:\\Methods\\method.dam",
            help="Select MS method file"
        )
        st.session_state.ms_method = ms_method
        
        plate_type = st.selectbox(
            "Plate Type",
            options=['1.5mL VT54 (54 vial)', 'MTP 96'],
            index=0 if st.session_state.plate_type == '1.5mL VT54 (54 vial)' else 1
        )
        st.session_state.plate_type = plate_type
        
        max_vials = 54 if plate_type == '1.5mL VT54 (54 vial)' else 96
    
    with col2:
        lc_method = st.text_input(
            "LC Method Path",
            value=st.session_state.lc_method,
            placeholder="D:\\Methods\\lc_method.lcm",
            help="Select LC method file"
        )
        st.session_state.lc_method = lc_method
        
        plate_number = st.selectbox(
            "Plate Number",
            options=[1, 2, 3],
            index=st.session_state.plate_number - 1
        )
        st.session_state.plate_number = plate_number
        
        injection_volume = st.number_input(
            "Injection Volume (µL)",
            min_value=0.01,
            max_value=100.0,
            value=st.session_state.injection_volume,
            step=0.1
        )
        st.session_state.injection_volume = injection_volume
    
    st.markdown(f"<br>**Sample Table** — Max vials: {max_vials} | Drag rows to reorder", unsafe_allow_html=True)
    
    data = []
    for i, item in enumerate(sequence):
        sample_name = generate_sample_name(item, st.session_state.naming_mode, sequence)
        data.append({
            'Sample Name': sample_name,
            'MS Method': ms_method,
            'LC Method': lc_method,
            'Rack Type': 'SIL-40 Drawer',
            'Plate Type': plate_type,
            'Plate Number': plate_number,
            'Vial Position': i + 1 if i + 1 <= max_vials else '',
            'Injection Volume': injection_volume,
            'Data File': f"{st.session_state.parent_folder}\\{sample_name}" if st.session_state.parent_folder else sample_name
        })
    
    df = pd.DataFrame(data)
    edited_df = render_aggrid(df, 'Sciex7500', 'sciex_grid')
    st.session_state.sequence_df = edited_df
    
    return edited_df


def render_agilent_config(sequence):
    """Render Agilent QQQ configuration and return DataFrame."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input(
            "Instrument Method Path",
            value=st.session_state.ms_method,
            placeholder="D:\\Methods\\method.m",
            help="MS method path"
        )
        st.session_state.ms_method = ms_method
    
    with col2:
        st.markdown("""
            <div class="alert alert-info" style="margin-top: 1.5rem;">
                <span class="alert-icon">📁</span>
                <span>Data Folder uses the path from Step 1</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>**Sample Table** — Position format: P1-A1 to P1-H12 | Drag rows to reorder", unsafe_allow_html=True)
    
    data = []
    for i, item in enumerate(sequence):
        sample_name = generate_sample_name(item, st.session_state.naming_mode, sequence)
        sample_type_map = {
            'Sample': 'Sample',
            'Standard': 'Sample',
            'QC': 'QC',
            'Blank': 'Blank'
        }
        sample_type = sample_type_map.get(item['type'], 'Sample')
        inj_vol = 'No injection' if sample_type == 'No injection' else 'As method'
        
        data.append({
            'Sample Name': sample_name,
            'Sample Position': '',
            'Method': ms_method,
            'Data Folder': st.session_state.parent_folder,
            'Data File': f"{sample_name}",
            'Sample Type': sample_type,
            'Injection Volume': inj_vol
        })
    
    df = pd.DataFrame(data)
    edited_df = render_aggrid(df, 'AgilentQQQ', 'agilent_grid')
    st.session_state.sequence_df = edited_df
    
    return edited_df


def render_hfx2_config(sequence):
    """Render HFX-2 configuration and return DataFrame."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input(
            "Instrument Method Path (.meth)",
            value=st.session_state.ms_method,
            placeholder="D:\\Methods\\method.meth",
            help="Must have .meth extension"
        )
        st.session_state.ms_method = ms_method
        
        if ms_method and not ms_method.endswith('.meth'):
            st.markdown("""
                <div class="alert alert-warning">
                    <span class="alert-icon">⚠️</span>
                    <span>Method file should have .meth extension</span>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        injection_volume = st.number_input(
            "Default Injection Volume (µL)",
            min_value=0.01,
            max_value=100.0,
            value=st.session_state.injection_volume,
            step=0.1
        )
        st.session_state.injection_volume = injection_volume
    
    st.markdown("<br>**Sample Table** — Position format: G:A1 to G:H12 | Drag rows to reorder", unsafe_allow_html=True)
    
    data = []
    for i, item in enumerate(sequence):
        sample_name = generate_sample_name(item, st.session_state.naming_mode, sequence)
        
        type_map = {
            'Sample': 'Unknown',
            'Standard': 'Std Bracket',
            'QC': 'QC',
            'Blank': 'Blank'
        }
        sample_type = type_map.get(item['type'], 'Unknown')
        needs_level = sample_type in ['QC', 'Std Bracket', 'Std Clear', 'Std Update']
        
        data.append({
            'Sample Type': sample_type,
            'File Name': f"{sample_name}.raw",
            'Sample ID': sample_name,
            'Path': st.session_state.parent_folder,
            'Instrument Method': ms_method,
            'Process Method': '',
            'Calibration File': '',
            'Position': '',
            'Inj Vol': injection_volume,
            'Level': 1 if needs_level else '',
            'Sample Wt': '' if not needs_level else 0.0,
            'Sample Vol': '',
            'ISTD Amt': '',
            'Dil Factor': 1,
            'L1 Study': '',
            'L2 Client': '',
            'L3 Laboratory': '',
            'L4 Company': '',
            'L5 Phone': '',
            'Comment': '',
            'Sample Name': sample_name
        })
    
    df = pd.DataFrame(data)
    edited_df = render_aggrid(df, 'HFX-2', 'hfx_grid')
    st.session_state.sequence_df = edited_df
    
    return edited_df


def validate_positions(df):
    """Validate for duplicate positions in the DataFrame."""
    if 'Vial Position' in df.columns:
        pos_col = 'Vial Position'
    elif 'Position' in df.columns:
        pos_col = 'Position'
    elif 'Sample Position' in df.columns:
        pos_col = 'Sample Position'
    else:
        return
    
    name_col = 'Sample Name' if 'Sample Name' in df.columns else df.columns[0]
    
    pos_groups = df.groupby(pos_col)[name_col].apply(list)
    duplicates = pos_groups[pos_groups.apply(len) > 1]
    
    if len(duplicates) > 0 and not duplicates.index.isin(['']).all():
        st.markdown("""
            <div class="alert alert-error">
                <span class="alert-icon">⚠️</span>
                <span><strong>Duplicate Position Warning:</strong> Multiple samples share the same position!</span>
            </div>
        """, unsafe_allow_html=True)
        for pos, names in duplicates.items():
            if pos and pos != '':
                st.warning(f"Position {pos}: {', '.join(str(n) for n in names)}")


def render_step5_export():
    """Render Step 5: Preview and Export."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-cyan">📤</div>
            <span>Step 5: Preview & Export</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.sequence_df is not None:
        df = st.session_state.sequence_df
        
        st.markdown("**Final Preview**")
        st.dataframe(df, use_container_width=True, height=400)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            include_headers = st.checkbox("Include column headers in CSV", value=False)
        
        with col2:
            filename = st.text_input(
                "Output filename",
                value=f"{st.session_state.project_name}.csv" if st.session_state.project_name else "batch.csv"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        csv_data = df.to_csv(index=False, header=include_headers)
        csv_with_headers = df.to_csv(index=False, header=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="📥 Download CSV (with headers)",
                data=csv_with_headers,
                file_name=f"headers_{filename}",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("""
            <div class="alert alert-success">
                <span class="alert-icon">✓</span>
                <span><strong>Ready to export!</strong> Click a download button above to save your batch file.</span>
            </div>
        """, unsafe_allow_html=True)
    
    if st.button("← Back to Configuration", key='back_5'):
        st.session_state.step = 4
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_footer():
    """Render the app footer."""
    st.markdown("""
        <div class="footer">
            <strong>MS Batch Generator</strong> v2.0 · Built with Streamlit<br>
            Supports Sciex7500 · AgilentQQQ · HFX-2
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Apply dark theme CSS
    st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content header
    st.markdown("""
        <div class="main-header-accent">Mass Spectrometry Batch Generator</div>
        <div class="subtitle">Generate CSV batch files for Sciex7500, AgilentQQQ, and HFX-2 instruments</div>
    """, unsafe_allow_html=True)
    
    # Render steps based on current progress
    if st.session_state.step >= 1:
        render_step1_initial_setup()
    
    if st.session_state.step >= 2:
        render_step2_sample_config()
    
    if st.session_state.step >= 3:
        render_step3_naming_rules()
    
    if st.session_state.step >= 4:
        render_step4_instrument_config()
    
    if st.session_state.step >= 5:
        render_step5_export()
    
    # Footer
    render_footer()


# Entry point
if __name__ == "__main__":
    main()
