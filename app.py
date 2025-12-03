"""
Instrument Batch/Worklist Generator
A Streamlit application for generating CSV batch files for mass spectrometry instruments.
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="MS Batch Generator",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS with modern lab/scientific aesthetic
st.markdown("""
<style>
    /* Import distinctive fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables for theming */
    :root {
        --primary: #0ea5e9;
        --primary-dark: #0284c7;
        --primary-light: #38bdf8;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --surface: #f8fafc;
        --surface-elevated: #ffffff;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #94a3b8;
        --border: #e2e8f0;
        --border-light: #f1f5f9;
    }
    
    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--border-light);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--text-muted);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
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
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 50%, #14b8a6 100%);
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
    
    /* Section cards */
    .section-card {
        background: var(--surface-elevated);
        border-radius: 16px;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
        transition: all 0.2s ease;
    }
    
    .section-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.04);
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
        border-bottom: 2px solid var(--border-light);
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
    
    .icon-blue { background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); }
    .icon-green { background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); }
    .icon-amber { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); }
    .icon-purple { background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%); }
    .icon-cyan { background: linear-gradient(135deg, #cffafe 0%, #a5f3fc 100%); }
    
    /* Progress stepper */
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
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        color: #047857;
    }
    
    .step-item.active {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        color: #1d4ed8;
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
        background: #10b981;
        color: white;
    }
    
    .step-item.active .step-number {
        background: #3b82f6;
        color: white;
    }
    
    .step-item.pending .step-number {
        background: var(--border);
        color: var(--text-muted);
    }
    
    /* Alert boxes */
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
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1px solid #fcd34d;
        color: #92400e;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 1px solid #93c5fd;
        color: #1e40af;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 1px solid #6ee7b7;
        color: #065f46;
    }
    
    .alert-error {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 1px solid #fca5a5;
        color: #991b1b;
    }
    
    /* Metric cards */
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
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
    
    /* Toggle switches styling */
    .toggle-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .toggle-item {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-secondary);
        transition: all 0.2s ease;
    }
    
    .toggle-item.active {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-color: var(--primary-light);
        color: var(--primary-dark);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.625rem 1.25rem;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
        color: white;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1px solid var(--border);
        font-family: 'DM Sans', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
    }
    
    /* Expander styling */
    div[data-testid="stExpander"] {
        background: var(--surface-elevated);
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }
    
    div[data-testid="stExpander"] > div:first-child {
        padding: 0.75rem 1rem;
    }
    
    /* Data editor */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid var(--border);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
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
        background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
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
    
    /* Code blocks */
    .code-preview {
        background: #1e293b;
        color: #e2e8f0;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    /* Footer */
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
    
    /* Instrument badges */
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
    
    .badge-sciex { background: #fef3c7; color: #92400e; }
    .badge-agilent { background: #dbeafe; color: #1e40af; }
    .badge-hfx { background: #ede9fe; color: #5b21b6; }
    
    /* Navigation buttons */
    .nav-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border-light);
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
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    defaults = {
        'step': 1,
        'instrument': None,
        'project_name': '',
        'parent_folder': '',
        'sample_types': {
            'standards': {'enabled': False, 'count': 0, 'rule': 'At the start only', 'interval': 1},
            'samples': {'enabled': True, 'count': 0, 'rule': 'At the start only', 'interval': 1},
            'qc': {'enabled': False, 'count': 0, 'rule': 'At fixed interval', 'interval': 10},
            'blanks': {'enabled': False, 'count': 0, 'rule': 'At fixed interval', 'interval': 5}
        },
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
            st.session_state[key] = value

init_session_state()

# Template management
TEMPLATES_FILE = 'saved_templates.json'

def load_templates():
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_template(name, config):
    templates = load_templates()
    templates[name] = config
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=2)

def delete_template(name):
    templates = load_templates()
    if name in templates:
        del templates[name]
        with open(TEMPLATES_FILE, 'w') as f:
            json.dump(templates, f, indent=2)

# Helper functions
def validate_project_name(name):
    """Validate project name format (e.g., MPG_25-12_GaIEMA)"""
    pattern = r'^[A-Za-z]{2,3}_\d{2}-\d{2}_\w+$'
    return bool(re.match(pattern, name)) if name else False

def generate_sequence(sample_types):
    """Generate the sample sequence based on frequency rules"""
    sequence = []
    
    # Get counts for each type
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
            # Check if we need to insert a blank before this sample
            if blank_interval > 0 and i > 1 and (i - 1) % blank_interval == 0:
                if blanks.get('enabled') and blank_placed < blanks.get('count', 0):
                    blank_counter += 1
                    blank_placed += 1
                    sequence.append({'type': 'Blank', 'index': blank_counter})
            
            # Check if we need to insert a QC before this sample
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

# Sidebar
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
    steps = [
        ('Initial Setup', '1'),
        ('Sample Config', '2'),
        ('Naming Rules', '3'),
        ('Instrument', '4'),
        ('Export', '5')
    ]
    current_step = st.session_state.step
    
    st.markdown('<div class="stepper-container">', unsafe_allow_html=True)
    for i, (step_name, step_num) in enumerate(steps, 1):
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
    
    st.markdown("---")
    
    # Template Management
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
                    st.session_state.sample_types = config.get('sample_types', st.session_state.sample_types)
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
    
    # Save current config as template
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
    
    st.markdown("---")
    
    # Clear all button
    if st.button("🗑️ Reset All", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main content area
st.markdown("""
    <div class="main-header-accent">Mass Spectrometry Batch Generator</div>
    <div class="subtitle">Generate CSV batch files for Sciex7500, AgilentQQQ, and HFX-2 instruments</div>
""", unsafe_allow_html=True)

# Step 1: Initial Setup
if st.session_state.step >= 1:
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
            options=['', 'Sciex7500', 'AgilentQQQ', 'HFX-2'],
            index=['', 'Sciex7500', 'AgilentQQQ', 'HFX-2'].index(st.session_state.instrument) if st.session_state.instrument else 0,
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

# Step 2: Sample Types Configuration
if st.session_state.step >= 2:
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
    
    # Configuration for active sample types
    st.markdown("<br>", unsafe_allow_html=True)
    
    frequency_rules = ['At the start only', 'At the end only', 'At fixed interval']
    
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
                            options=frequency_rules,
                            index=frequency_rules.index(config['rule']) if config['rule'] in frequency_rules else 0,
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

# Step 3: Sample Naming Rules
if st.session_state.step >= 3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-amber">✏️</div>
            <span>Step 3: Sample Naming Rules</span>
        </div>
    """, unsafe_allow_html=True)
    
    naming_modes = ['None', 'Auto-build (Prefix + Index + Suffix)', 'Enter each name manually', 'Import from CSV/Excel']
    
    naming_mode = st.selectbox(
        "Naming Mode",
        options=naming_modes,
        index=naming_modes.index(st.session_state.naming_mode) if st.session_state.naming_mode in naming_modes else 0
    )
    st.session_state.naming_mode = naming_mode
    
    if naming_mode == 'Auto-build (Prefix + Index + Suffix)':
        st.markdown("""
            <div class="alert alert-info">
                <span class="alert-icon">💡</span>
                <span>Names are generated as <code style="background: rgba(0,0,0,0.1); padding: 0.2rem 0.4rem; border-radius: 4px;">Prefix_Index_Suffix</code> (e.g., Matrix_1_dil)</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Column order selection
        col_order = st.multiselect(
            "Name Component Order",
            options=['Prefix', 'Index', 'Suffix'],
            default=['Prefix', 'Index', 'Suffix'],
            help="Reorder how name parts are combined"
        )
        
        # Configure naming for each sample type
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
                    
                    # Preview
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

# Step 4: Instrument-Specific Configuration
if st.session_state.step >= 4:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    # Instrument badge
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
    
    # Generate base sequence
    sequence = generate_sequence(st.session_state.sample_types)
    
    # Generate sample names based on naming mode
    def generate_sample_name(item, naming_mode):
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
            total_idx = sum(1 for s in sequence[:sequence.index(item)] if s['type'] == item['type'])
            if total_idx < len(names):
                return names[total_idx]
        
        return f"{item['type']}{idx}"
    
    # SCIEX 7500 Configuration
    if st.session_state.instrument == 'Sciex7500':
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
        
        # Build the data table
        st.markdown(f"<br>**Sample Table** — Max vials: {max_vials}", unsafe_allow_html=True)
        
        data = []
        for i, item in enumerate(sequence):
            sample_name = generate_sample_name(item, st.session_state.naming_mode)
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
        
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Vial Position": st.column_config.NumberColumn(
                    "Vial Position",
                    min_value=1,
                    max_value=max_vials,
                    help=f"Valid range: 1-{max_vials}"
                ),
                "Injection Volume": st.column_config.NumberColumn(
                    "Injection Volume",
                    min_value=0.01,
                    max_value=100.0,
                    format="%.2f"
                )
            }
        )
        
        st.session_state.sequence_df = edited_df
    
    # Agilent QQQ Configuration
    elif st.session_state.instrument == 'AgilentQQQ':
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
        
        st.markdown("<br>**Sample Table** — Position format: P1-A1 to P1-H12", unsafe_allow_html=True)
        
        data = []
        for i, item in enumerate(sequence):
            sample_name = generate_sample_name(item, st.session_state.naming_mode)
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
        
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Sample Position": st.column_config.TextColumn(
                    "Sample Position",
                    help="Format: P1-A1",
                    max_chars=10
                ),
                "Sample Type": st.column_config.SelectboxColumn(
                    "Sample Type",
                    options=['No injection', 'Blank', 'Sample', 'QC'],
                    required=True
                ),
                "Injection Volume": st.column_config.SelectboxColumn(
                    "Injection Volume",
                    options=['No injection', 'As method'],
                    required=True
                )
            }
        )
        
        st.session_state.sequence_df = edited_df
    
    # HFX-2 Configuration
    elif st.session_state.instrument == 'HFX-2':
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
        
        st.markdown("<br>**Sample Table** — Position format: G:A1 to G:H12", unsafe_allow_html=True)
        
        data = []
        for i, item in enumerate(sequence):
            sample_name = generate_sample_name(item, st.session_state.naming_mode)
            
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
        
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Sample Type": st.column_config.SelectboxColumn(
                    "Sample Type",
                    options=['Blank', 'Unknown', 'QC', 'Std Bracket', 'Std Update', 'Std Clear', 'Start Bracket'],
                    required=True
                ),
                "Position": st.column_config.TextColumn(
                    "Position",
                    help="Format: G:A1 to G:H12"
                ),
                "Inj Vol": st.column_config.NumberColumn(
                    "Inj Vol",
                    min_value=0.01,
                    max_value=100.0,
                    format="%.2f"
                ),
                "Level": st.column_config.NumberColumn("Level"),
                "Sample Wt": st.column_config.NumberColumn("Sample Wt"),
                "Dil Factor": st.column_config.NumberColumn("Dil Factor", default=1)
            }
        )
        
        st.session_state.sequence_df = edited_df
    
    # Validation warnings
    if st.session_state.sequence_df is not None:
        df = st.session_state.sequence_df
        
        if 'Vial Position' in df.columns:
            pos_col = 'Vial Position'
        elif 'Position' in df.columns:
            pos_col = 'Position'
        elif 'Sample Position' in df.columns:
            pos_col = 'Sample Position'
        else:
            pos_col = None
        
        if pos_col:
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

# Step 5: Preview and Export
if st.session_state.step >= 5:
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
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            include_headers = st.checkbox("Include column headers in CSV", value=False)
        
        with col2:
            filename = st.text_input(
                "Output filename",
                value=f"{st.session_state.project_name}.csv" if st.session_state.project_name else "batch.csv"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Generate CSV
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

# Footer
st.markdown("""
    <div class="footer">
        <strong>MS Batch Generator</strong> v1.0 · Built with Streamlit<br>
        Supports Sciex7500 · AgilentQQQ · HFX-2
    </div>
""", unsafe_allow_html=True)
