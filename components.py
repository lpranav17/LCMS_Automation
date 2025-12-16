"""
UI Components for MS Batch Generator
"""

import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items

from config import (
    INSTRUMENTS, FREQUENCY_RULES, NAMING_MODES, STEPS,
    AGILENT_SAMPLE_TYPES, AGILENT_INJ_OPTIONS, HFX_SAMPLE_TYPES
)
from utils import (
    reset_session_state, generate_sequence, generate_sample_name
)


# ============================================================================
# TABLE HELPER FUNCTIONS
# ============================================================================

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


# ============================================================================
# SIDEBAR COMPONENTS
# ============================================================================

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


# ============================================================================
# STEP 1: INITIAL SETUP
# ============================================================================

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


# ============================================================================
# STEP 2: SAMPLE CONFIGURATION
# ============================================================================

def render_step2_sample_config():
    """Render Step 2: Sample Types Configuration."""
    st.subheader("🧫 Step 2: Sample Configuration")
    
    # Initialize order if not present
    if 'sample_type_order' not in st.session_state:
        st.session_state.sample_type_order = ['standards', 'samples', 'qc', 'blanks']
    
    type_labels = {'standards': 'Standards', 'samples': 'Samples', 'qc': 'QC', 'blanks': 'Blanks'}
    
    # === ENABLE TOGGLES ===
    st.markdown("**Enable Sample Types:**")
    cols = st.columns(4)
    with cols[0]:
        st.session_state.sample_types['standards']['enabled'] = st.checkbox("Standards", value=st.session_state.sample_types['standards']['enabled'])
    with cols[1]:
        st.session_state.sample_types['samples']['enabled'] = st.checkbox("Samples", value=st.session_state.sample_types['samples']['enabled'])
    with cols[2]:
        st.session_state.sample_types['qc']['enabled'] = st.checkbox("QC", value=st.session_state.sample_types['qc']['enabled'])
    with cols[3]:
        st.session_state.sample_types['blanks']['enabled'] = st.checkbox("Blanks", value=st.session_state.sample_types['blanks']['enabled'])
    
    # === SEQUENCE ORDER (drag and drop) ===
    enabled_types = [t for t in st.session_state.sample_type_order if st.session_state.sample_types[t]['enabled']]
    
    if len(enabled_types) > 1:
        st.markdown("---")
        st.markdown("**🔀 Sequence Order** *(drag to reorder)*")
        
        # Simple text labels for better readability
        key_to_label = {
            'standards': 'Standards', 
            'samples': 'Samples', 
            'qc': 'QC', 
            'blanks': 'Blanks'
        }
        label_to_key = {v: k for k, v in key_to_label.items()}
        
        # Get current order as labels
        current_labels = [key_to_label[k] for k in enabled_types]
        
        # Drag and drop sortable
        sorted_labels = sort_items(current_labels, direction="horizontal")
        
        # Convert back to keys
        sorted_enabled = [label_to_key[label] for label in sorted_labels]
        
        # Update session state
        disabled_types = [t for t in st.session_state.sample_type_order if not st.session_state.sample_types[t]['enabled']]
        st.session_state.sample_type_order = sorted_enabled + disabled_types
        
        # Show order preview
        st.info(f"**Run order:** {' → '.join(sorted_labels)}")
    
    st.markdown("---")
    
    # === CONFIGURE EACH TYPE ===
    active_types = [(name, st.session_state.sample_types[name]) for name in st.session_state.sample_type_order if st.session_state.sample_types[name]['enabled']]
    
    for type_name, config in active_types:
        st.markdown(f"**{type_labels[type_name]}**")
        
        if type_name == 'samples':
            # Samples only need count
            count = st.number_input("Count", min_value=0, max_value=500, value=config['count'], key=f"count_{type_name}")
            st.session_state.sample_types[type_name]['count'] = count
        else:
            # Other types: count, rule, interval
            c1, c2, c3 = st.columns(3)
            with c1:
                count = st.number_input("Count", min_value=0, max_value=500, value=config['count'], key=f"count_{type_name}")
                st.session_state.sample_types[type_name]['count'] = count
            with c2:
                rule = st.selectbox("Rule", options=FREQUENCY_RULES, index=FREQUENCY_RULES.index(config['rule']) if config['rule'] in FREQUENCY_RULES else 0, key=f"rule_{type_name}")
                st.session_state.sample_types[type_name]['rule'] = rule
            with c3:
                current_rule = st.session_state.sample_types[type_name].get('rule', '')
                if current_rule in ['At fixed interval', 'At start + fixed interval']:
                    interval = st.number_input("Every N samples", min_value=1, max_value=100, value=config.get('interval', 5), key=f"interval_{type_name}")
                    st.session_state.sample_types[type_name]['interval'] = interval
            
            # Start count for "At start + fixed interval"
            if current_rule == 'At start + fixed interval' and count > 0:
                max_start = max(1, count)
                current_start = min(config.get('start_count', count), max_start)
                start_count = st.number_input("How many at start?", min_value=1, max_value=max_start, value=current_start, key=f"start_count_{type_name}")
                st.session_state.sample_types[type_name]['start_count'] = start_count
        
        st.markdown("---")
    
    # === SUMMARY ===
    if any(config['enabled'] and config['count'] > 0 for config in st.session_state.sample_types.values()):
        sequence = generate_sequence(st.session_state.sample_types, st.session_state.get('sample_type_order'))
        st.markdown("**Sequence Summary**")
        summary = {}
        for item in sequence:
            summary[item['type']] = summary.get(item['type'], 0) + 1
        
        summary_cols = st.columns(len(summary) + 1)
        with summary_cols[0]:
            st.metric("Total", len(sequence))
        for i, (stype, cnt) in enumerate(summary.items(), 1):
            with summary_cols[i]:
                st.metric(stype, cnt)
    
    # === NAVIGATION ===
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key='back_2'):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if any(config['enabled'] and config['count'] > 0 for config in st.session_state.sample_types.values()):
            if st.button("Continue to Naming →", key='next_2', type="primary"):
                st.session_state.step = max(st.session_state.step, 3)
                st.rerun()
    
    st.markdown("---")


# ============================================================================
# STEP 3: NAMING RULES
# ============================================================================

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
                        prefix = st.text_input("Prefix", value=type_name[:3].upper() if type_name != 'samples' else 'SPL', key=f"prefix_{type_name}", help="e.g., STD, SPL, QC, BLK")
                    with cols[1]:
                        st.number_input("Start Index", min_value=1, value=1, key=f"index_start_{type_name}", help="Starting number for samples")
                    with cols[2]:
                        st.text_input("Suffix (optional)", value="", key=f"suffix_{type_name}", placeholder="e.g., uM, dil, prep1", help="e.g., 10uM, dil2, batch1")
                    
                    # Show preview
                    prefix_val = st.session_state.get(f"prefix_{type_name}", type_name[:3].upper())
                    idx_val = st.session_state.get(f"index_start_{type_name}", 1)
                    suffix_val = st.session_state.get(f"suffix_{type_name}", "")
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


# ============================================================================
# STEP 4: INSTRUMENT CONFIGURATION
# ============================================================================

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


def render_agilent_config(sequence):
    """Render Agilent QQQ configuration."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input("Instrument Method", value=st.session_state.ms_method, placeholder="D:\\Methods\\method.m")
        st.session_state.ms_method = ms_method
    with col2:
        st.info("📁 Data Folder from Step 1")
    
    st.markdown("**Sample Table** — Position format: P1-A1 to P1-H12")
    
    if not sequence:
        st.warning("⚠️ No samples configured. Go back to Step 2 to add samples.")
        return None
    
    data = []
    for i, item in enumerate(sequence):
        sample_name = generate_sample_name(item, st.session_state.naming_mode, sequence)
        sample_type = {'Sample': 'Sample', 'Standard': 'Sample', 'QC': 'QC', 'Blank': 'Blank'}.get(item['type'], 'Sample')
        data.append({
            'Sample Name': sample_name,
            'Sample Position': '',
            'Method': ms_method,
            'Data Folder': st.session_state.parent_folder,
            'Data File': sample_name,
            'Sample Type': sample_type,
            'Injection Volume': 'As method'
        })
    
    df = pd.DataFrame(data)
    
    # Check if sequence changed - reset stored DataFrame
    seq_hash = hash(tuple([item['type'] + str(item['index']) for item in sequence]))
    if st.session_state.get('agilent_seq_hash') != seq_hash:
        st.session_state['agilent_seq_hash'] = seq_hash
        st.session_state['agilent_needs_reset'] = True
    
    st.caption("💡 **Double-click** cells to edit")
    
    edited_df = render_editable_table(df, key_prefix='agilent', height=400)
    st.session_state.sequence_df = edited_df
    return edited_df


def render_hfx2_config(sequence):
    """Render HFX-2 configuration with full column format."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input("Instrument Method (.meth)", value=st.session_state.ms_method, placeholder="D:\\Methods\\method.meth")
        st.session_state.ms_method = ms_method
        if ms_method and not ms_method.endswith('.meth'):
            st.warning("⚠️ Should have .meth extension")
    with col2:
        injection_volume = st.number_input("Injection Volume (µL)", min_value=0.01, max_value=100.0, value=st.session_state.injection_volume, step=0.1)
        st.session_state.injection_volume = injection_volume
    
    st.markdown("**Sample Table** — Position format: G:A1 to G:H12")
    
    if not sequence:
        st.warning("⚠️ No samples configured. Go back to Step 2 to add samples.")
        return None
    
    # HFX-2 full column format (matching instrument requirements)
    data = []
    for i, item in enumerate(sequence):
        sample_name = generate_sample_name(item, st.session_state.naming_mode, sequence)
        sample_type = {'Sample': 'Unknown', 'Standard': 'Std Bracket', 'QC': 'QC', 'Blank': 'Blank'}.get(item['type'], 'Unknown')
        needs_level = sample_type in ['QC', 'Std Bracket', 'Std Update', 'Std Clear']
        
        data.append({
            'Sample Type': sample_type,
            'File Name': f"{sample_name}.raw",
            'Sample ID': sample_name,
            'Path': st.session_state.parent_folder,
            'Instrument Method': ms_method,
            'Position': '',
            'Inj Vol': injection_volume,
            'Dil Factor': 1,
            'Sample Name': sample_name
        })
    
    df = pd.DataFrame(data)
    
    # Check if sequence changed - reset stored DataFrame
    seq_hash = hash(tuple([item['type'] + str(item['index']) for item in sequence]))
    if st.session_state.get('hfx_seq_hash') != seq_hash:
        st.session_state['hfx_seq_hash'] = seq_hash
        st.session_state['hfx_needs_reset'] = True
    
    st.caption("💡 **Double-click** cells to edit")
    
    edited_df = render_editable_table(df, key_prefix='hfx', height=400)
    
    # Build full DataFrame for export with all HFX columns
    full_data = []
    for i, row in edited_df.iterrows():
        full_row = {
            'Sample Type': row.get('Sample Type', 'Unknown'),
            'File Name': row.get('File Name', ''),
            'Sample ID': row.get('Sample ID', ''),
            'Path': row.get('Path', st.session_state.parent_folder),
            'Instrument Method': row.get('Instrument Method', ms_method),
            'Process Method': '',
            'Calibration File': '',
            'Position': row.get('Position', ''),
            'Inj Vol': row.get('Inj Vol', injection_volume),
            'Level': 1 if row.get('Sample Type', '') in ['QC', 'Std Bracket', 'Std Update', 'Std Clear'] else '',
            'Sample Wt': '',
            'Sample Vol': '',
            'ISTD Amt': '',
            'Dil Factor': row.get('Dil Factor', 1),
            'L1 Study': '',
            'L2 Client': '',
            'L3 Laboratory': '',
            'L4 Company': '',
            'L5 Phone': '',
            'Comment': '',
            'Sample Name': row.get('Sample Name', '')
        }
        full_data.append(full_row)
    
    full_df = pd.DataFrame(full_data)
    st.session_state.sequence_df = full_df
    return full_df


# ============================================================================
# STEP 5: EXPORT
# ============================================================================

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


def render_footer():
    """Render the app footer."""
    st.markdown("""
        <div class="footer">
            <strong>MS Batch Generator</strong> v2.0 · Built with Streamlit<br>
            Supports Sciex7500 · AgilentQQQ · HFX-2
        </div>
    """, unsafe_allow_html=True)

