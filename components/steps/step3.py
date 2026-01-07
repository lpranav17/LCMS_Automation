"""
Step 3: Naming Rules
"""

import streamlit as st
import pandas as pd
from config import NAMING_MODES


def render_step3_naming_rules():
    """Render Step 3: Sample Naming Rules."""
    st.subheader("✏️ Step 3: Sample Naming Rules")
    
    naming_mode = st.selectbox("Naming Mode", options=NAMING_MODES, index=NAMING_MODES.index(st.session_state.naming_mode) if st.session_state.naming_mode in NAMING_MODES else 0)
    st.session_state.naming_mode = naming_mode
    
    if naming_mode == 'Auto-build (Prefix + Index + Suffix)':
        st.markdown('<div class="alert alert-info">💡 Names: Prefix_Index_Suffix (e.g., SPL_1_dil)</div>', unsafe_allow_html=True)
        
        for type_name, config in st.session_state.sample_types.items():
            if config['enabled'] and config['count'] > 0:
                with st.expander(f"🏷️ {type_name.title()} Naming", expanded=True):
                    cols = st.columns(3)
                    with cols[0]:
                        default_prefix = type_name[:3].upper() if type_name != 'samples' else 'SPL'
                        prefix = st.text_input("Prefix", value=st.session_state.get(f"prefix_{type_name}", default_prefix), key=f"prefix_{type_name}", help="e.g., STD, SPL, QC, BLK")
                        # Update session state immediately
                        st.session_state[f"prefix_{type_name}"] = prefix
                    with cols[1]:
                        index_start = st.number_input("Start Index", min_value=1, value=st.session_state.get(f"index_start_{type_name}", 1), key=f"index_start_{type_name}", help="Starting number for samples")
                        # Update session state immediately
                        st.session_state[f"index_start_{type_name}"] = index_start
                    with cols[2]:
                        suffix = st.text_input("Suffix (optional)", value=st.session_state.get(f"suffix_{type_name}", ""), key=f"suffix_{type_name}", placeholder="e.g., uM, dil, prep1", help="e.g., 10uM, dil2, batch1")
                        # Update session state immediately
                        st.session_state[f"suffix_{type_name}"] = suffix
                    
                    # Show preview using current values (updates on the fly)
                    prefix_val = prefix if prefix else default_prefix
                    idx_val = index_start
                    suffix_val = suffix
                    preview = f"{prefix_val}_{idx_val}_{suffix_val}" if suffix_val else f"{prefix_val}_{idx_val}"
                    st.markdown(f'<div class="code-preview">Preview: {preview}, {prefix_val}_{idx_val+1}{"_"+suffix_val if suffix_val else ""}, ...</div>', unsafe_allow_html=True)
    
    elif naming_mode == 'Import from CSV/Excel':
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.dataframe(df.head(), use_container_width=True)
                name_column = st.selectbox("Select column with sample names", options=df.columns.tolist())
                if name_column:
                    st.session_state.imported_names = df[name_column].tolist()
                    st.markdown(f'<div class="alert alert-success">✓ Imported {len(st.session_state.imported_names)} names</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="alert alert-error">✕ Error: {e}</div>', unsafe_allow_html=True)
    
    elif naming_mode == 'None':
        st.markdown('<div class="alert alert-info">📝 Auto-numbered: Sample1, Sample2, QC1, etc.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key='back_3'):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Continue to Instrument →", key='next_3', type="primary"):
            st.session_state.step = max(st.session_state.step, 4)
            st.rerun()
    
    st.markdown("---")

