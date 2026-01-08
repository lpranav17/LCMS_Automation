"""
Step 4: Instrument Configuration
"""

import streamlit as st
from datetime import datetime, timedelta
from utils import generate_sequence, calculate_sequence_runtime, format_runtime
from components.instruments import render_sciex7500_config, render_agilent_config, render_hfx2_config


def render_step4_instrument_config():
    """Render Step 4: Instrument-Specific Configuration."""
    st.subheader(f"⚙️ Step 4: Instrument Configuration ({st.session_state.instrument})")
    
    sequence = generate_sequence(st.session_state.sample_types, st.session_state.get('sample_type_order'))
    
    # Method runtime input (common for all instruments)
    st.markdown("**Method Runtime**")
    method_runtime = st.number_input(
        "Method Runtime (minutes)",
        min_value=0.0,
        max_value=1000.0,
        value=st.session_state.get('method_runtime', 0.0),
        step=0.1,
        help="Enter the runtime of your method per injection in minutes"
    )
    st.session_state.method_runtime = method_runtime
    
    st.markdown("---")
    
    if st.session_state.instrument == 'Sciex7500':
        df = render_sciex7500_config(sequence)
    elif st.session_state.instrument == 'AgilentQQQ':
        df = render_agilent_config(sequence)
    elif st.session_state.instrument == 'HFX-2':
        df = render_hfx2_config(sequence)
    else:
        df = None
    
    # Display runtime estimates if we have a sequence and method runtime
    if df is not None and len(sequence) > 0 and method_runtime > 0:
        st.markdown("---")
        st.markdown("**⏱️ Runtime Estimates**")
        
        sequence_length = len(sequence)
        total_runtime_minutes = calculate_sequence_runtime(sequence_length, method_runtime, handover_minutes=1.0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estimated Sequence Run Time", format_runtime(total_runtime_minutes))
        
        with col2:
            if total_runtime_minutes > 0:
                # Create a real-time updating finish time display
                st.markdown("**Estimated Time to Finish**")
                finish_time_container = st.empty()
                
                # JavaScript to recalculate finish time in real-time based on current time + runtime
                finish_time_html = f"""
                <div id="finish-time-display" style="font-size: 2rem; font-weight: bold; color: #1f77b4; padding: 0.5rem 0;">
                    <span id="finish-time-value">--:--:--</span>
                </div>
                <script>
                    (function() {{
                        const runtimeMinutes = {total_runtime_minutes};
                        
                        function updateFinishTime() {{
                            const now = new Date();
                            const finishTime = new Date(now.getTime() + runtimeMinutes * 60 * 1000);
                            
                            const hours = String(finishTime.getHours()).padStart(2, '0');
                            const minutes = String(finishTime.getMinutes()).padStart(2, '0');
                            const seconds = String(finishTime.getSeconds()).padStart(2, '0');
                            document.getElementById('finish-time-value').textContent = hours + ':' + minutes + ':' + seconds;
                        }}
                        
                        // Update immediately and then every second
                        updateFinishTime();
                        setInterval(updateFinishTime, 1000);
                    }})();
                </script>
                """
                finish_time_container.markdown(finish_time_html, unsafe_allow_html=True)
        
        st.info("ℹ️ **Note:** Assumes 1 minute handover time between injections. Total time = (Method Runtime + 1 min) × Number of Samples")
    
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

