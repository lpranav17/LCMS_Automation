"""
Sidebar components
"""

import streamlit as st
from utils import reset_session_state
from components.common.stepper import render_progress_stepper


def render_sidebar():
    """Render the sidebar with navigation."""
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-header">
                <div class="sidebar-logo">⚗️</div>
                <div>
                    <div class="sidebar-title">MS Batch Gen</div>
                    <div class="sidebar-subtitle">Worklist Generator</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        render_progress_stepper()
        st.markdown("---")
        
        # Help Manual
        with st.expander("📖 **How to Use**", expanded=False):
            st.markdown("""
            **Step 1: Initial Setup**
            - Select your instrument (Sciex7500, AgilentQQQ, or HFX-2)
            - Enter project name and data folder path
            
            **Step 2: Sample Configuration**
            - Enable sample types: Standards, Samples, QC, Blanks
            - Set count and placement rules for each
            - **Drag & drop** to reorder sequence
            - Rules:
              - *At start only*: Appears once at beginning
              - *At end only*: Appears once at end
              - *At fixed interval*: Repeats every N samples
            
            **Step 3: Naming Rules**
            - Choose naming mode (Auto-build, Manual, Import)
            - Configure prefixes and suffixes
            
            **Step 4: Instrument Config**
            - Configure instrument-specific settings
            - **Row controls:**
              - Select row number
              - ⬆️ Move row up
              - ⬇️ Move row down
              - ⭐ Highlight row (yellow)
            - Double-click cells to edit
            
            **Step 5: Export**
            - Preview final sequence
            - Download as CSV
            
            ---
            💡 **Tips:**
            - Use Reset All to start fresh
            - Highlighted rows appear in yellow
            - All changes save automatically
            """)
        
        st.markdown("---")
        
        if st.button("🗑️ Reset All", use_container_width=True, type="secondary"):
            reset_session_state()
            st.rerun()


def render_footer():
    """Render the app footer."""
    st.markdown("""
        <div class="footer">
            <strong>MS Batch Generator</strong> v2.0 · Built with Streamlit<br>
            Supports Sciex7500 · AgilentQQQ · HFX-2
        </div>
    """, unsafe_allow_html=True)

