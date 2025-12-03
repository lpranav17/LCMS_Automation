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
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, modern look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1a365d;
        margin-bottom: 0.5rem;
        border-bottom: 3px solid #3182ce;
        padding-bottom: 0.5rem;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 500;
        color: #2c5282;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background: linear-gradient(90deg, #ebf8ff 0%, transparent 100%);
        border-left: 4px solid #3182ce;
    }
    
    .step-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .warning-box {
        background-color: #fffaf0;
        border: 1px solid #ed8936;
        border-left: 4px solid #ed8936;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #ebf8ff;
        border: 1px solid #3182ce;
        border-left: 4px solid #3182ce;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #f0fff4;
        border: 1px solid #38a169;
        border-left: 4px solid #38a169;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
    }
    
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-weight: 500;
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
    
    # Add remaining standards at start if rule is "At the start only"
    if standards.get('enabled') and standards.get('rule') == 'At the start only':
        # Already added above
        pass
    
    return sequence

def autofill_name_pattern(existing_names):
    """Try to detect naming pattern from existing names"""
    if len(existing_names) < 2:
        return None
    
    # Try to find numeric suffix pattern
    pattern = r'^(.+?)(\d+)$'
    matches = [re.match(pattern, name) for name in existing_names if name]
    
    if all(matches) and matches:
        prefix = matches[0].group(1)
        last_num = max(int(m.group(2)) for m in matches if m)
        return f"{prefix}{last_num + 1}"
    
    return None

# Sidebar - Template Management & Navigation
with st.sidebar:
    st.markdown('<div class="main-header">🧪 MS Batch Gen</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Progress indicator
    steps = ['Setup', 'Sample Config', 'Naming', 'Instrument', 'Preview']
    current_step = st.session_state.step
    
    for i, step_name in enumerate(steps, 1):
        if i < current_step:
            st.markdown(f"✅ **Step {i}:** {step_name}")
        elif i == current_step:
            st.markdown(f"🔵 **Step {i}:** {step_name}")
        else:
            st.markdown(f"⚪ Step {i}: {step_name}")
    
    st.markdown("---")
    
    # Template Management
    st.markdown("### 📁 Templates")
    
    templates = load_templates()
    
    if templates:
        selected_template = st.selectbox(
            "Load Template",
            options=[''] + list(templates.keys()),
            key='template_select'
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load", disabled=not selected_template):
                if selected_template:
                    config = templates[selected_template]
                    st.session_state.sample_types = config.get('sample_types', st.session_state.sample_types)
                    st.session_state.naming_mode = config.get('naming_mode', 'None')
                    st.rerun()
        with col2:
            if st.button("Delete", disabled=not selected_template):
                if selected_template:
                    delete_template(selected_template)
                    st.rerun()
    
    # Save current config as template
    with st.expander("Save as Template"):
        template_name = st.text_input("Template Name", key='new_template_name')
        if st.button("Save Template", disabled=not template_name):
            config = {
                'sample_types': st.session_state.sample_types,
                'naming_mode': st.session_state.naming_mode,
            }
            save_template(template_name, config)
            st.success(f"Saved '{template_name}'!")
            st.rerun()
    
    st.markdown("---")
    
    # Clear all button
    if st.button("🗑️ Clear All", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main content area
st.markdown('<div class="main-header">Instrument Batch/Worklist Generator</div>', unsafe_allow_html=True)

# Step 1: Initial Setup
if st.session_state.step >= 1:
    st.markdown('<div class="section-header">📋 Step 1: Initial Setup</div>', unsafe_allow_html=True)
    
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
            "Project Name (Worklist/Batch File Name)",
            value=st.session_state.project_name,
            placeholder="e.g., MPG_25-12_GaIEMA",
            help="Format: 2-3 letter initials_YY-MM_ProjectCode"
        )
        st.session_state.project_name = project_name
        
        if project_name and not validate_project_name(project_name):
            st.warning("⚠️ Project name doesn't match recommended format (e.g., MPG_25-12_GaIEMA)")
    
    with col2:
        parent_folder = st.text_input(
            "Parent Folder Path",
            value=st.session_state.parent_folder,
            placeholder="D:\\Data\\Project_Folder",
            help="Path where all data files and CSV batch file will be saved"
        )
        st.session_state.parent_folder = parent_folder
        
        if parent_folder:
            if st.session_state.instrument == 'AgilentQQQ' and not parent_folder.upper().startswith('D:'):
                st.warning("⚠️ AgilentQQQ requires folder path on D: drive")
    
    # Navigation
    if st.session_state.instrument and project_name:
        if st.button("Next: Sample Configuration →", key='next_1'):
            st.session_state.step = max(st.session_state.step, 2)
            st.rerun()

# Step 2: Sample Types Configuration
if st.session_state.step >= 2:
    st.markdown('<div class="section-header">🧫 Step 2: Sample Types & Frequency Rules</div>', unsafe_allow_html=True)
    
    # Sample type toggles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.session_state.sample_types['standards']['enabled'] = st.toggle(
            "Standards",
            value=st.session_state.sample_types['standards']['enabled']
        )
    with col2:
        st.session_state.sample_types['samples']['enabled'] = st.toggle(
            "Samples",
            value=st.session_state.sample_types['samples']['enabled']
        )
    with col3:
        st.session_state.sample_types['qc']['enabled'] = st.toggle(
            "Quality Controls (QCs)",
            value=st.session_state.sample_types['qc']['enabled']
        )
    with col4:
        st.session_state.sample_types['blanks']['enabled'] = st.toggle(
            "Blanks",
            value=st.session_state.sample_types['blanks']['enabled']
        )
    
    # Warning if no QC or blanks
    if not st.session_state.sample_types['qc']['enabled'] and not st.session_state.sample_types['blanks']['enabled']:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Warning:</strong> No QC or Blank samples selected. 
            Consider adding these for quality assurance.
        </div>
        """, unsafe_allow_html=True)
    
    # Configuration table for active sample types
    st.markdown("#### Configuration Table")
    
    frequency_rules = ['At the start only', 'At the end only', 'At fixed interval']
    
    active_types = [(name, config) for name, config in st.session_state.sample_types.items() if config['enabled']]
    
    if active_types:
        for type_name, config in active_types:
            with st.expander(f"📌 {type_name.title()}", expanded=True):
                cols = st.columns([2, 2, 2])
                
                with cols[0]:
                    count = st.number_input(
                        f"Count",
                        min_value=0,
                        max_value=500,
                        value=config['count'],
                        key=f"count_{type_name}"
                    )
                    st.session_state.sample_types[type_name]['count'] = count
                
                with cols[1]:
                    if type_name != 'samples':
                        rule = st.selectbox(
                            f"Frequency Rule",
                            options=frequency_rules,
                            index=frequency_rules.index(config['rule']) if config['rule'] in frequency_rules else 0,
                            key=f"rule_{type_name}"
                        )
                        st.session_state.sample_types[type_name]['rule'] = rule
                    else:
                        st.info("Samples form the main sequence")
                
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
        
        st.markdown("#### 📊 Sequence Preview")
        summary = {}
        for item in sequence:
            summary[item['type']] = summary.get(item['type'], 0) + 1
        
        cols = st.columns(len(summary) + 1)
        cols[0].metric("Total Injections", len(sequence))
        for i, (stype, count) in enumerate(summary.items(), 1):
            cols[i].metric(stype, count)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Setup", key='back_2'):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if any(config['enabled'] and config['count'] > 0 for config in st.session_state.sample_types.values()):
            if st.button("Next: Naming Rules →", key='next_2'):
                st.session_state.step = max(st.session_state.step, 3)
                st.rerun()

# Step 3: Sample Naming Rules
if st.session_state.step >= 3:
    st.markdown('<div class="section-header">✏️ Step 3: Sample Naming Rules</div>', unsafe_allow_html=True)
    
    naming_modes = ['None', 'Auto-build (Prefix + Index + Suffix)', 'Enter each name manually', 'Import from CSV/Excel']
    
    naming_mode = st.selectbox(
        "Naming Mode",
        options=naming_modes,
        index=naming_modes.index(st.session_state.naming_mode) if st.session_state.naming_mode in naming_modes else 0
    )
    st.session_state.naming_mode = naming_mode
    
    if naming_mode == 'Auto-build (Prefix + Index + Suffix)':
        st.markdown("""
        <div class="info-box">
            💡 <strong>Auto-build:</strong> Names are generated as <code>Prefix_Index_Suffix</code> (e.g., Matrix_dil_5)
        </div>
        """, unsafe_allow_html=True)
        
        # Column order selection
        col_order = st.multiselect(
            "Column Order (drag to reorder)",
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
                            placeholder="e.g., uM, 5"
                        )
                    
                    # Preview
                    if prefix:
                        parts = {'Prefix': prefix, 'Index': str(index_start), 'Suffix': suffix}
                        sample_name = '_'.join([parts[c] for c in col_order if parts.get(c)])
                        st.code(f"Example: {sample_name}")
    
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
                
                st.write("Preview of uploaded file:")
                st.dataframe(df.head())
                
                name_column = st.selectbox(
                    "Select column containing sample names",
                    options=df.columns.tolist()
                )
                
                if name_column:
                    st.session_state.imported_names = df[name_column].tolist()
                    st.success(f"Imported {len(st.session_state.imported_names)} sample names")
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    elif naming_mode == 'None':
        st.markdown("""
        <div class="info-box">
            📝 Samples will be automatically numbered: Sample1, Sample2, QC1, Blank1, etc.
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Sample Config", key='back_3'):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Next: Instrument Configuration →", key='next_3'):
            st.session_state.step = max(st.session_state.step, 4)
            st.rerun()

# Step 4: Instrument-Specific Configuration
if st.session_state.step >= 4:
    st.markdown(f'<div class="section-header">⚙️ Step 4: {st.session_state.instrument} Configuration</div>', unsafe_allow_html=True)
    
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
        st.markdown("### Sciex7500 Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            ms_method = st.text_input(
                "MS Method Path",
                value=st.session_state.ms_method,
                placeholder="D:\\Methods\\method.dam",
                help="Select MS method file from drive"
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
                help="Select LC method file from drive"
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
        st.markdown("### Sample Table")
        st.markdown(f"*Max vials for selected plate: {max_vials}*")
        
        # Create DataFrame
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
        
        # Editable table
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
        st.markdown("### AgilentQQQ Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            ms_method = st.text_input(
                "Instrument Method Path",
                value=st.session_state.ms_method,
                placeholder="D:\\Methods\\method.m",
                help="MS method path (same for all samples)"
            )
            st.session_state.ms_method = ms_method
        
        with col2:
            st.info("📁 Data Folder will use the parent folder path from Step 1")
        
        # Build the data table
        st.markdown("### Sample Table")
        st.markdown("*Sample Position format: P1-A1 to P1-H12*")
        
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
                    help="Format: P1-A1 (auto-corrects p1a1 to P1-A1)",
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
        st.markdown("### HFX-2 Settings")
        
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
                st.warning("⚠️ Method file should have .meth extension")
        
        with col2:
            injection_volume = st.number_input(
                "Default Injection Volume (µL)",
                min_value=0.01,
                max_value=100.0,
                value=st.session_state.injection_volume,
                step=0.1
            )
            st.session_state.injection_volume = injection_volume
        
        # Build the data table
        st.markdown("### Sample Table")
        st.markdown("*Vial Position format: G:A1 to G:H12*")
        
        data = []
        for i, item in enumerate(sequence):
            sample_name = generate_sample_name(item, st.session_state.naming_mode)
            
            # Map sample types for HFX-2
            type_map = {
                'Sample': 'Unknown',
                'Standard': 'Std Bracket',
                'QC': 'QC',
                'Blank': 'Blank'
            }
            sample_type = type_map.get(item['type'], 'Unknown')
            
            # Level and Sample Weight are needed for certain types
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
        
        # Check for duplicate vial positions with different names
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
            
            # Find duplicates
            pos_groups = df.groupby(pos_col)[name_col].apply(list)
            duplicates = pos_groups[pos_groups.apply(len) > 1]
            
            if len(duplicates) > 0 and not duplicates.index.isin(['']).all():
                st.markdown("""
                <div class="warning-box">
                    ⚠️ <strong>Duplicate Position Warning:</strong> Multiple samples have the same vial/plate position!
                </div>
                """, unsafe_allow_html=True)
                for pos, names in duplicates.items():
                    if pos and pos != '':
                        st.warning(f"Position {pos}: {', '.join(str(n) for n in names)}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Naming Rules", key='back_4'):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Next: Preview & Export →", key='next_4'):
            st.session_state.step = max(st.session_state.step, 5)
            st.rerun()

# Step 5: Preview and Export
if st.session_state.step >= 5:
    st.markdown('<div class="section-header">📤 Step 5: Preview & Export</div>', unsafe_allow_html=True)
    
    if st.session_state.sequence_df is not None:
        df = st.session_state.sequence_df
        
        st.markdown("### Final Preview")
        st.dataframe(df, use_container_width=True)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            include_headers = st.checkbox("Include column headers in CSV", value=False)
        
        with col2:
            filename = st.text_input(
                "Output filename",
                value=f"{st.session_state.project_name}.csv" if st.session_state.project_name else "batch.csv"
            )
        
        # Generate CSV
        csv_data = df.to_csv(index=False, header=include_headers)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
        
        # Also offer with headers version
        csv_with_headers = df.to_csv(index=False, header=True)
        st.download_button(
            label="📥 Download CSV (with headers)",
            data=csv_with_headers,
            file_name=f"headers_{filename}",
            mime="text/csv",
            use_container_width=True
        )
        
        st.markdown("""
        <div class="success-box">
            ✅ <strong>Ready to export!</strong> Click the download button to save your batch file.
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("← Back to Configuration", key='back_5'):
        st.session_state.step = 4
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #718096; font-size: 0.85rem;'>"
    "MS Batch Generator v1.0 | Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)

