"""
Utility functions for MS Batch Generator
"""

import streamlit as st
import json
import os
import re
from config import TEMPLATES_FILE, DEFAULT_SAMPLE_TYPES


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
# VALIDATION FUNCTIONS
# ============================================================================

def validate_project_name(name):
    """Validate project name format (e.g., MPG_25-12_GaIEMA)."""
    pattern = r'^[A-Za-z]{2,3}_\d{2}-\d{2}_\w+$'
    return bool(re.match(pattern, name)) if name else False


# ============================================================================
# SEQUENCE GENERATION
# ============================================================================

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

