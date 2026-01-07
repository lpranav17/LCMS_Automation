"""
Sciex7500 instrument configuration
"""

import streamlit as st
import pandas as pd
from utils import generate_sample_name
from components.common.table import render_editable_table


def render_sciex7500_config(sequence):
    """Render Sciex7500 configuration."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input("MS Method Path", value=st.session_state.ms_method, placeholder="D:\\Methods\\method.dam")
        st.session_state.ms_method = ms_method
        plate_type = st.selectbox("Plate Type", options=['1.5mL VT54 (54 vial)', 'MTP 96'], index=0 if st.session_state.plate_type == '1.5mL VT54 (54 vial)' else 1)
        st.session_state.plate_type = plate_type
        max_vials = 54 if plate_type == '1.5mL VT54 (54 vial)' else 96
    
    with col2:
        lc_method = st.text_input("LC Method Path", value=st.session_state.lc_method, placeholder="D:\\Methods\\lc_method.lcm")
        st.session_state.lc_method = lc_method
        plate_number = st.selectbox("Plate Number", options=[1, 2, 3], index=st.session_state.plate_number - 1)
        st.session_state.plate_number = plate_number
        injection_volume = st.number_input("Injection Volume (µL)", min_value=0.01, max_value=100.0, value=st.session_state.injection_volume, step=0.1)
        st.session_state.injection_volume = injection_volume
    
    st.markdown(f"**Sample Table** — Max vials: {max_vials}")
    
    if not sequence:
        st.warning("⚠️ No samples configured. Go back to Step 2 to add samples.")
        return None
    
    # Build initial DataFrame from sequence
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
            'Vial Position': i + 1 if i + 1 <= max_vials else 1,
            'Injection Volume': injection_volume,
            'Data File': f"{st.session_state.parent_folder}\\{sample_name}" if st.session_state.parent_folder else sample_name
        })
    
    df = pd.DataFrame(data)
    
    # Check if sequence changed - reset stored DataFrame
    seq_hash = hash(tuple([item['type'] + str(item['index']) for item in sequence]))
    if st.session_state.get('sciex_seq_hash') != seq_hash:
        st.session_state['sciex_seq_hash'] = seq_hash
        st.session_state['sciex_needs_reset'] = True
    
    st.caption("💡 **Double-click** cells to edit")
    
    edited_df = render_editable_table(df, key_prefix='sciex', height=400)
    st.session_state.sequence_df = edited_df
    return edited_df
