"""
Step 1: Initial Setup
"""

import streamlit as st
from config import INSTRUMENTS


def render_step1_initial_setup():
    """Render Step 1: Initial Setup."""
    st.subheader("📋 Step 1: Initial Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_idx = INSTRUMENTS.index(st.session_state.instrument) if st.session_state.instrument in INSTRUMENTS else None
        instrument = st.selectbox(
            "Select Instrument",
            options=INSTRUMENTS,
            index=current_idx,
            placeholder="Choose an instrument..."
        )
        st.session_state.instrument = instrument
        
        project_name = st.text_input(
            "Project Name",
            value=st.session_state.project_name,
            placeholder="e.g., MPG_25-12_GaIEMA",
            help="Suggested format: XX_YY-MM_Name (e.g., MPG_25-12_GaIEMA)"
        )
        st.session_state.project_name = project_name
    
    with col2:
        parent_folder = st.text_input(
            "Data Folder Path",
            value=st.session_state.parent_folder,
            placeholder="D:\\Data\\Project_Folder"
        )
        st.session_state.parent_folder = parent_folder
        
        if parent_folder and st.session_state.instrument == 'AgilentQQQ' and not parent_folder.upper().startswith('D:'):
            st.warning("⚠️ AgilentQQQ requires D: drive")
    
    if st.session_state.instrument and project_name:
        if st.button("Continue to Sample Configuration →", key='next_1', type="primary"):
            st.session_state.step = max(st.session_state.step, 2)
            st.rerun()
    
    st.markdown("---")

