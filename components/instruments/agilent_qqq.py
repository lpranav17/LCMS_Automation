"""
Agilent QQQ instrument configuration
"""

import streamlit as st
import pandas as pd
from utils import generate_sample_name
from components.common.table import render_editable_table


def render_agilent_config(sequence):
    """Render Agilent QQQ configuration."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input("Instrument Method", value=st.session_state.ms_method, placeholder="D:\\Methods\\method.m")
        st.session_state.ms_method = ms_method
    with col2:
        st.info("📁 Data Folder from Step 1")
    
    st.markdown("**Sample Table** — Position format: P1-A1 to P1-H12")
    
    if not sequence:
        st.warning("⚠️ No samples configured. Go back to Step 2 to add samples.")
        return None
    
    data = []
    for i, item in enumerate(sequence):
        sample_name = generate_sample_name(item, st.session_state.naming_mode, sequence)
        sample_type = {'Sample': 'Sample', 'Standard': 'Sample', 'QC': 'QC', 'Blank': 'Blank'}.get(item['type'], 'Sample')
        data.append({
            'Sample Name': sample_name,
            'Sample Position': '',
            'Method': ms_method,
            'Data Folder': st.session_state.parent_folder,
            'Data File': sample_name,
            'Sample Type': sample_type,
            'Injection Volume': 'As method'
        })
    
    df = pd.DataFrame(data)
    
    # Check if sequence changed - reset stored DataFrame
    seq_hash = hash(tuple([item['type'] + str(item['index']) for item in sequence]))
    if st.session_state.get('agilent_seq_hash') != seq_hash:
        st.session_state['agilent_seq_hash'] = seq_hash
        st.session_state['agilent_needs_reset'] = True
    
    # Check if config values changed (method, parent folder) - reset stored DataFrame
    config_hash = hash((ms_method, st.session_state.parent_folder))
    if st.session_state.get('agilent_config_hash') != config_hash:
        st.session_state['agilent_config_hash'] = config_hash
        st.session_state['agilent_needs_reset'] = True
    
    st.caption("💡 **Double-click** cells to edit")
    
    edited_df = render_editable_table(df, key_prefix='agilent', height=400)
    st.session_state.sequence_df = edited_df
    return edited_df
