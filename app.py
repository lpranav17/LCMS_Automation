"""
MS Batch Generator - Main Application
A Streamlit app for generating CSV batch files for mass spectrometry instruments.
"""

import streamlit as st

from config import PAGE_CONFIG
from styles import get_dark_theme_css
from utils import init_session_state
from components import (
    render_sidebar,
    render_step1_initial_setup,
    render_step2_sample_config,
    render_step3_naming_rules,
    render_step4_instrument_config,
    render_step5_export,
    render_footer
)


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Apply dark theme CSS
    st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content header
    st.markdown("""
        <div class="main-header-accent">Mass Spectrometry Batch Generator</div>
        <div class="subtitle">Generate CSV batch files for Sciex7500, AgilentQQQ, and HFX-2 instruments</div>
    """, unsafe_allow_html=True)
    
    # Render steps based on current progress
    if st.session_state.step >= 1:
        render_step1_initial_setup()
    
    if st.session_state.step >= 2:
        render_step2_sample_config()
    
    if st.session_state.step >= 3:
        render_step3_naming_rules()
    
    if st.session_state.step >= 4:
        render_step4_instrument_config()
    
    if st.session_state.step >= 5:
        render_step5_export()
    
    # Footer
    render_footer()


if __name__ == "__main__":
    main()
