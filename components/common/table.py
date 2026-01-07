"""
Editable table component
"""

import streamlit as st


def render_editable_table(df, key_prefix, column_config=None, height=400):
    """
    Render a simple editable table.
    
    Args:
        df: DataFrame to display
        key_prefix: Unique key prefix for this table
        column_config: Optional column configuration for st.data_editor
        height: Table height in pixels
    
    Returns:
        Edited DataFrame
    """
    df_key = f"{key_prefix}_df"
    
    # Store DataFrame in session state for persistence
    if df_key not in st.session_state or st.session_state.get(f"{key_prefix}_needs_reset", False):
        st.session_state[df_key] = df.copy()
        st.session_state[f"{key_prefix}_needs_reset"] = False
    
    # Get working DataFrame
    working_df = st.session_state[df_key].copy()
    
    # Add row number column
    display_df = working_df.copy()
    display_df.insert(0, '#', range(1, len(display_df) + 1))
    
    # Build column config
    full_config = {'#': st.column_config.NumberColumn('#', disabled=True, width="small")}
    if column_config:
        full_config.update(column_config)
    
    # Editable table
    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic",
        use_container_width=True,
        height=height,
        key=f"{key_prefix}_editor",
        column_config=full_config,
        hide_index=True
    )
    
    # Update stored DataFrame (remove # column)
    if '#' in edited_df.columns:
        edited_df = edited_df.drop(columns=['#'])
    
    st.session_state[df_key] = edited_df.reset_index(drop=True)
    
    return edited_df
