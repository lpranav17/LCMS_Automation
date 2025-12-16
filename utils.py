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
        'sample_type_order': ['standards', 'samples', 'qc', 'blanks'],  # Default order
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

def generate_sequence(sample_types, type_order=None):
    """
    Generate the sample sequence based on frequency rules.
    
    Rules:
    - At the start only: Place 'count' items at beginning only (e.g., QC1, QC2)
    - At the end only: Place 'count' items at the end only
    - At fixed interval: Place 'count' items at START, then repeat after every N samples
      Example with count=2, interval=5: QC1, QC2, S1-S5, QC1, QC2, S6-S10, QC1, QC2...
    - At start + fixed interval: Same with configurable start count
    
    For interval rules, 'count' = how many items at EACH occurrence (repeating with reset indices)
    
    Args:
        sample_types: Dict of sample type configurations
        type_order: List defining order of types (default: ['standards', 'samples', 'qc', 'blanks'])
    """
    sequence = []
    
    # Default order if not specified
    if type_order is None:
        type_order = ['standards', 'samples', 'qc', 'blanks']
    
    # Map type names to display names
    type_display = {
        'standards': 'Standard',
        'samples': 'Sample', 
        'qc': 'QC',
        'blanks': 'Blank'
    }
    
    # Get all type configs
    type_configs = {
        'standards': sample_types.get('standards', {}),
        'samples': sample_types.get('samples', {}),
        'qc': sample_types.get('qc', {}),
        'blanks': sample_types.get('blanks', {})
    }
    
    def includes_interval(rule):
        return rule in ['At fixed interval', 'At start + fixed interval']
    
    # Helper to add a repeating block (indices reset: 1, 2, 3... each time)
    def add_block(stype, count, sequence):
        for i in range(1, count + 1):
            sequence.append({'type': stype, 'index': i})
    
    # Get interval settings for interval-based types
    interval_types = {}  # type_key -> (interval, count)
    for type_key in type_order:
        config = type_configs.get(type_key, {})
        if config.get('enabled') and includes_interval(config.get('rule', '')):
            interval_types[type_key] = (config.get('interval', 0), config.get('count', 0))
    
    # === START ITEMS (in order) ===
    for type_key in type_order:
        config = type_configs.get(type_key, {})
        display_name = type_display.get(type_key, type_key.title())
        
        if not config.get('enabled'):
            continue
            
        rule = config.get('rule', '')
        
        # "At the start only" - add full count at start
        if rule == 'At the start only':
            add_block(display_name, config.get('count', 0), sequence)
        
        # "At start + fixed interval" - add configurable start count
        elif rule == 'At start + fixed interval':
            start_count = config.get('start_count', config.get('count', 0))
            add_block(display_name, start_count, sequence)
        
        # "At fixed interval" - add initial block at start
        elif rule == 'At fixed interval':
            add_block(display_name, config.get('count', 0), sequence)
    
    # === MAIN SEQUENCE (in order) ===
    sample_counter = 0
    
    # Find main sequence types (not start-only, not end-only, not interval-only)
    main_types = []
    for type_key in type_order:
        config = type_configs.get(type_key, {})
        if config.get('enabled'):
            rule = config.get('rule', '')
            # samples is always main, others only if they have interval-based rules
            if type_key == 'samples' or rule not in ['At the start only', 'At the end only', 'At fixed interval', 'At start + fixed interval']:
                main_types.append(type_key)
    
    # Process main sequence types
    for type_key in main_types:
        config = type_configs.get(type_key, {})
        display_name = type_display.get(type_key, type_key.title())
        item_count = config.get('count', 0)
        
        for i in range(1, item_count + 1):
            sequence.append({'type': display_name, 'index': i})
            sample_counter += 1
            
            # Add interval blocks after every N items (in order)
            for interval_key in type_order:
                if interval_key in interval_types:
                    interval, count = interval_types[interval_key]
                    if interval > 0 and sample_counter % interval == 0:
                        add_block(type_display.get(interval_key, interval_key.title()), count, sequence)
    
    # === END ITEMS (in order) ===
    for type_key in type_order:
        config = type_configs.get(type_key, {})
        display_name = type_display.get(type_key, type_key.title())
        
        if config.get('enabled') and config.get('rule') == 'At the end only':
            add_block(display_name, config.get('count', 0), sequence)
    
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

