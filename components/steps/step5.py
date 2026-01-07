"""
Step 5: Export
"""

import streamlit as st


def render_step5_export():
    """Render Step 5: Preview and Export."""
    st.subheader("📤 Step 5: Preview & Export")
    
    if st.session_state.sequence_df is not None:
        df = st.session_state.sequence_df
        
        st.markdown("**Final Preview**")
        st.dataframe(df, use_container_width=True, height=400)
        
        col1, col2 = st.columns(2)
        with col1:
            include_headers = st.checkbox("Include column headers", value=False)
        with col2:
            filename = st.text_input("Output filename", value=f"{st.session_state.project_name}.csv" if st.session_state.project_name else "batch.csv")
        
        csv_data = df.to_csv(index=False, header=include_headers)
        csv_with_headers = df.to_csv(index=False, header=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Download CSV", data=csv_data, file_name=filename, mime="text/csv", use_container_width=True)
        with col2:
            st.download_button("📥 Download (with headers)", data=csv_with_headers, file_name=f"headers_{filename}", mime="text/csv", use_container_width=True)
        
        st.success("✓ Ready to export!")
    
    if st.button("← Back to Configuration", key='back_5'):
        st.session_state.step = 4
        st.rerun()
