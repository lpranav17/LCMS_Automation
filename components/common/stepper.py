"""
Progress stepper component
"""

import streamlit as st
from config import STEPS


def render_progress_stepper():
    """Render the step progress indicator."""
    current_step = st.session_state.step
    
    st.markdown('<div class="stepper-container">', unsafe_allow_html=True)
    for i, (step_name, step_num) in enumerate(STEPS, 1):
        if i < current_step:
            status, icon = "completed", "✓"
        elif i == current_step:
            status, icon = "active", step_num
        else:
            status, icon = "pending", step_num
        
        st.markdown(f"""
            <div class="step-item {status}">
                <div class="step-number">{icon}</div>
                <span>{step_name}</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

