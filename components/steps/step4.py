"""
Step 4: Instrument Configuration
"""

import streamlit as st
from utils import generate_sequence
from components.instruments import render_sciex7500_config, render_agilent_config, render_hfx2_config


def render_step4_instrument_config():
    """Render Step 4: Instrument-Specific Configuration."""
    st.subheader(f"⚙️ Step 4: Instrument Configuration ({st.session_state.instrument})")
    
    sequence = generate_sequence(st.session_state.sample_types, st.session_state.get('sample_type_order'))
    
    if st.session_state.instrument == 'Sciex7500':
        df = render_sciex7500_config(sequence)
    elif st.session_state.instrument == 'AgilentQQQ':
        df = render_agilent_config(sequence)
    elif st.session_state.instrument == 'HFX-2':
        df = render_hfx2_config(sequence)
    else:
        df = None
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key='back_4'):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Continue to Export →", key='next_4', type="primary"):
            st.session_state.step = max(st.session_state.step, 5)
            st.rerun()
    
    st.markdown("---")
