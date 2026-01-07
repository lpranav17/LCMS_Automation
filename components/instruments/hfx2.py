"""
HFX-2 instrument configuration
"""

import streamlit as st
import pandas as pd
from utils import generate_sample_name
from components.common.table import render_editable_table


def render_hfx2_config(sequence):
    """Render HFX-2 configuration with full column format."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input("Instrument Method (.meth)", value=st.session_state.ms_method, placeholder="D:\\Methods\\method.meth")
        st.session_state.ms_method = ms_method
        if ms_method and not ms_method.endswith('.meth'):
            st.warning("⚠️ Should have .meth extension")
    with col2:
        injection_volume = st.number_input("Injection Volume (µL)", min_value=0.01, max_value=100.0, value=st.session_state.injection_volume, step=0.1)
        st.session_state.injection_volume = injection_volume
    
    st.markdown("**Sample Table** — Position format: G:A1 to G:H12")
    
    if not sequence:
        st.warning("⚠️ No samples configured. Go back to Step 2 to add samples.")
        return None
    
    # HFX-2 full column format (matching instrument requirements)
    data = []
    for i, item in enumerate(sequence):
        sample_name = generate_sample_name(item, st.session_state.naming_mode, sequence)
        sample_type = {'Sample': 'Unknown', 'Standard': 'Std Bracket', 'QC': 'QC', 'Blank': 'Blank'}.get(item['type'], 'Unknown')
        needs_level = sample_type in ['QC', 'Std Bracket', 'Std Update', 'Std Clear']
        
        data.append({
            'Sample Type': sample_type,
            'File Name': f"{sample_name}.raw",
            'Sample ID': sample_name,
            'Path': st.session_state.parent_folder,
            'Instrument Method': ms_method,
            'Position': '',
            'Inj Vol': injection_volume,
            'Dil Factor': 1,
            'Sample Name': sample_name
        })
    
    df = pd.DataFrame(data)
    
    # Check if sequence changed - reset stored DataFrame
    seq_hash = hash(tuple([item['type'] + str(item['index']) for item in sequence]))
    if st.session_state.get('hfx_seq_hash') != seq_hash:
        st.session_state['hfx_seq_hash'] = seq_hash
        st.session_state['hfx_needs_reset'] = True
    
    st.caption("💡 **Double-click** cells to edit")
    
    edited_df = render_editable_table(df, key_prefix='hfx', height=400)
    
    # Build full DataFrame for export with all HFX columns
    full_data = []
    for i, row in edited_df.iterrows():
        full_row = {
            'Sample Type': row.get('Sample Type', 'Unknown'),
            'File Name': row.get('File Name', ''),
            'Sample ID': row.get('Sample ID', ''),
            'Path': row.get('Path', st.session_state.parent_folder),
            'Instrument Method': row.get('Instrument Method', ms_method),
            'Process Method': '',
            'Calibration File': '',
            'Position': row.get('Position', ''),
            'Inj Vol': row.get('Inj Vol', injection_volume),
            'Level': 1 if row.get('Sample Type', '') in ['QC', 'Std Bracket', 'Std Update', 'Std Clear'] else '',
            'Sample Wt': '',
            'Sample Vol': '',
            'ISTD Amt': '',
            'Dil Factor': row.get('Dil Factor', 1),
            'L1 Study': '',
            'L2 Client': '',
            'L3 Laboratory': '',
            'L4 Company': '',
            'L5 Phone': '',
            'Comment': '',
            'Sample Name': row.get('Sample Name', '')
        }
        full_data.append(full_row)
    
    full_df = pd.DataFrame(full_data)
    st.session_state.sequence_df = full_df
    return full_df

