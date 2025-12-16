"""
UI Components for MS Batch Generator
"""

import streamlit as st
import pandas as pd

from config import (
    INSTRUMENTS, FREQUENCY_RULES, NAMING_MODES, STEPS,
    DEFAULT_SAMPLE_TYPES, AGILENT_SAMPLE_TYPES, AGILENT_INJ_OPTIONS, HFX_SAMPLE_TYPES
)
from utils import (
    load_templates, save_template, delete_template, reset_session_state,
    generate_sequence, generate_sample_name
)


# ============================================================================
# SIDEBAR COMPONENTS
# ============================================================================

def render_sidebar():
    """Render the sidebar with navigation and template management."""
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
        render_template_management()
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


def render_template_management():
    """Render template save/load functionality."""
    st.markdown('<div class="template-title">📁 Saved Templates</div>', unsafe_allow_html=True)
    
    templates = load_templates()
    
    if templates:
        selected_template = st.selectbox(
            "Select Template",
            options=[''] + list(templates.keys()),
            key='template_select',
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load", disabled=not selected_template, use_container_width=True):
                if selected_template:
                    config = templates[selected_template]
                    st.session_state.sample_types = config.get('sample_types', DEFAULT_SAMPLE_TYPES.copy())
                    st.session_state.naming_mode = config.get('naming_mode', 'None')
                    st.rerun()
        with col2:
            if st.button("Delete", disabled=not selected_template, use_container_width=True):
                if selected_template:
                    delete_template(selected_template)
                    st.rerun()
    else:
        st.markdown('<div style="color: #94a3b8; font-size: 0.85rem;">No templates saved yet</div>', unsafe_allow_html=True)
    
    with st.expander("💾 Save New Template"):
        template_name = st.text_input("Template Name", key='new_template_name', placeholder="My Template")
        if st.button("Save Template", disabled=not template_name, use_container_width=True):
            config = {
                'sample_types': st.session_state.sample_types,
                'naming_mode': st.session_state.naming_mode,
            }
            save_template(template_name, config)
            st.success(f"✓ Saved '{template_name}'")
            st.rerun()


# ============================================================================
# STEP 1: INITIAL SETUP
# ============================================================================

def render_step1_initial_setup():
    """Render Step 1: Initial Setup."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-blue">📋</div>
            <span>Step 1: Initial Setup</span>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        instrument = st.selectbox(
            "Select Instrument",
            options=INSTRUMENTS,
            index=INSTRUMENTS.index(st.session_state.instrument) if st.session_state.instrument else 0
        )
        st.session_state.instrument = instrument if instrument else None
        
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
            st.markdown('<div class="alert alert-warning">⚠️ AgilentQQQ requires D: drive</div>', unsafe_allow_html=True)
    
    if st.session_state.instrument and project_name:
        if st.button("Continue to Sample Configuration →", key='next_1', type="primary"):
            st.session_state.step = max(st.session_state.step, 2)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# STEP 2: SAMPLE CONFIGURATION
# ============================================================================

def render_step2_sample_config():
    """Render Step 2: Sample Types Configuration."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-green">🧫</div>
            <span>Step 2: Sample Types & Frequency Rules</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize order if not present
    if 'sample_type_order' not in st.session_state:
        st.session_state.sample_type_order = ['standards', 'samples', 'qc', 'blanks']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.session_state.sample_types['standards']['enabled'] = st.toggle("📊 Standards", value=st.session_state.sample_types['standards']['enabled'])
    with col2:
        st.session_state.sample_types['samples']['enabled'] = st.toggle("🧪 Samples", value=st.session_state.sample_types['samples']['enabled'])
    with col3:
        st.session_state.sample_types['qc']['enabled'] = st.toggle("✓ QC", value=st.session_state.sample_types['qc']['enabled'])
    with col4:
        st.session_state.sample_types['blanks']['enabled'] = st.toggle("○ Blanks", value=st.session_state.sample_types['blanks']['enabled'])
    
    if not st.session_state.sample_types['qc']['enabled'] and not st.session_state.sample_types['blanks']['enabled']:
        st.markdown('<div class="alert alert-warning">💡 Consider adding QC or Blanks for quality assurance</div>', unsafe_allow_html=True)
    
    # === SEQUENCE ORDER SECTION ===
    st.markdown("---")
    st.markdown("##### 🔀 Sequence Order")
    st.markdown('<div style="font-size:0.85em;color:#666;margin-bottom:0.5rem;">Drag to reorder how sample types appear in the sequence</div>', unsafe_allow_html=True)
    
    type_icons = {'standards': '📊', 'samples': '🧪', 'qc': '✓', 'blanks': '○'}
    type_labels = {'standards': 'Standards', 'samples': 'Samples', 'qc': 'QC', 'blanks': 'Blanks'}
    
    order_cols = st.columns([3, 1, 1, 3])
    
    with order_cols[0]:
        for idx, type_key in enumerate(st.session_state.sample_type_order):
            enabled = st.session_state.sample_types[type_key]['enabled']
            icon = type_icons.get(type_key, '•')
            label = type_labels.get(type_key, type_key.title())
            style = "" if enabled else "opacity:0.4;"
            st.markdown(f'<div style="padding:0.3rem 0.5rem;margin:2px 0;background:#f0f2f6;border-radius:4px;{style}">{idx+1}. {icon} {label}</div>', unsafe_allow_html=True)
    
    with order_cols[1]:
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        for idx in range(len(st.session_state.sample_type_order)):
            if st.button("⬆", key=f"up_{idx}", disabled=(idx == 0)):
                order = st.session_state.sample_type_order
                order[idx], order[idx-1] = order[idx-1], order[idx]
                st.rerun()
    
    with order_cols[2]:
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        for idx in range(len(st.session_state.sample_type_order)):
            if st.button("⬇", key=f"down_{idx}", disabled=(idx == len(st.session_state.sample_type_order) - 1)):
                order = st.session_state.sample_type_order
                order[idx], order[idx+1] = order[idx+1], order[idx]
                st.rerun()
    
    with order_cols[3]:
        # Show current order preview
        enabled_order = [type_labels[t] for t in st.session_state.sample_type_order if st.session_state.sample_types[t]['enabled']]
        if enabled_order:
            st.markdown(f'<div style="font-size:0.85em;color:#666;padding-top:0.5rem;">Order: {" → ".join(enabled_order)}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get active types in the specified order
    active_types = [(name, st.session_state.sample_types[name]) for name in st.session_state.sample_type_order if st.session_state.sample_types[name]['enabled']]
    
    for type_name, config in active_types:
        with st.expander(f"⚙️ Configure {type_name.title()}", expanded=True):
            cols = st.columns([2, 2, 2])
            
            with cols[0]:
                current_rule = config.get('rule', '')
                help_text = f"How many {type_name} at each occurrence" if current_rule in ['At fixed interval', 'At start + fixed interval'] else f"Total number of {type_name}"
                count = st.number_input(f"Count per block", min_value=0, max_value=500, value=config['count'], key=f"count_{type_name}", help=help_text)
                st.session_state.sample_types[type_name]['count'] = count
            
            with cols[1]:
                if type_name != 'samples':
                    rule = st.selectbox("Placement Rule", options=FREQUENCY_RULES, index=FREQUENCY_RULES.index(config['rule']) if config['rule'] in FREQUENCY_RULES else 0, key=f"rule_{type_name}")
                    st.session_state.sample_types[type_name]['rule'] = rule
                else:
                    st.markdown('<div class="alert alert-info" style="margin:0;padding:0.5rem;">Main sequence</div>', unsafe_allow_html=True)
            
            with cols[2]:
                current_rule = st.session_state.sample_types[type_name].get('rule', '')
                if type_name != 'samples' and current_rule in ['At fixed interval', 'At start + fixed interval']:
                    interval = st.number_input(
                        "Every N samples", 
                        min_value=1, 
                        max_value=100, 
                        value=config.get('interval', 5), 
                        key=f"interval_{type_name}",
                        help=f"Places {count} {type_name} at start, then repeats after every N samples"
                    )
                    st.session_state.sample_types[type_name]['interval'] = interval
            
            # Show example pattern for interval rules
            if type_name != 'samples' and current_rule == 'At fixed interval' and count > 0:
                interval_val = config.get('interval', 5)
                example = f"Pattern: {type_name[0].upper()}1"
                if count > 1:
                    example += f"-{type_name[0].upper()}{count}"
                example += f" → S1-S{interval_val} → {type_name[0].upper()}1"
                if count > 1:
                    example += f"-{type_name[0].upper()}{count}"
                example += " → ..."
                st.markdown(f'<div class="alert alert-info" style="margin:0;padding:0.5rem;font-size:0.85em;">{example}</div>', unsafe_allow_html=True)
            
            # Additional row for "At start + fixed interval" to set how many at start
            if type_name != 'samples' and st.session_state.sample_types[type_name].get('rule') == 'At start + fixed interval':
                st.markdown("---")
                col_start = st.columns([2, 2, 2])
                with col_start[0]:
                    start_count = st.number_input(
                        f"How many at start?", 
                        min_value=1, 
                        max_value=max(1, config.get('count', 2)), 
                        value=config.get('start_count', config.get('count', 2)), 
                        key=f"start_count_{type_name}",
                        help="Number to place at the beginning of the sequence"
                    )
                    st.session_state.sample_types[type_name]['start_count'] = start_count
                with col_start[1]:
                    interval_val = config.get('interval', 5)
                    st.markdown(f'<div class="alert alert-info" style="margin:0;padding:0.5rem;">Then {count} every {interval_val} samples</div>', unsafe_allow_html=True)
    
    if any(config['enabled'] and config['count'] > 0 for config in st.session_state.sample_types.values()):
        sequence = generate_sequence(st.session_state.sample_types, st.session_state.get('sample_type_order'))
        st.markdown("#### 📊 Sequence Summary")
        summary = {}
        for item in sequence:
            summary[item['type']] = summary.get(item['type'], 0) + 1
        cols = st.columns(len(summary) + 1)
        with cols[0]:
            st.metric("Total", len(sequence))
        for i, (stype, count) in enumerate(summary.items(), 1):
            with cols[i]:
                st.metric(stype, count)
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# STEP 3: NAMING RULES
# ============================================================================

def render_step3_naming_rules():
    """Render Step 3: Sample Naming Rules."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-amber">✏️</div>
            <span>Step 3: Sample Naming Rules</span>
        </div>
    """, unsafe_allow_html=True)
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# STEP 4: INSTRUMENT CONFIGURATION
# ============================================================================

def render_step4_instrument_config():
    """Render Step 4: Instrument-Specific Configuration."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    badge_class = {'Sciex7500': 'badge-sciex', 'AgilentQQQ': 'badge-agilent', 'HFX-2': 'badge-hfx'}.get(st.session_state.instrument, 'badge-sciex')
    
    st.markdown(f"""
        <div class="section-header">
            <div class="section-icon icon-purple">⚙️</div>
            <span>Step 4: Instrument Configuration</span>
        </div>
        <div class="instrument-badge {badge_class}">🔬 {st.session_state.instrument}</div>
    """, unsafe_allow_html=True)
    
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
    
    st.markdown('</div>', unsafe_allow_html=True)


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
        st.markdown('<div class="alert alert-warning">⚠️ No samples configured. Go back to Step 2 to add samples.</div>', unsafe_allow_html=True)
        return None
    
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
    
    st.markdown('<div class="alert alert-info">💡 Double-click cells to edit • Add rows with + button • Drag columns to resize</div>', unsafe_allow_html=True)
    
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic", 
        use_container_width=True, 
        height=400, 
        key='sciex_editor',
        column_config={
            "Vial Position": st.column_config.NumberColumn("Vial Position", min_value=1, max_value=max_vials),
            "Injection Volume": st.column_config.NumberColumn("Injection Volume", min_value=0.01, format="%.2f"),
            "Plate Number": st.column_config.NumberColumn("Plate Number", min_value=1, max_value=3)
        }
    )
    st.session_state.sequence_df = edited_df
    return edited_df


def render_agilent_config(sequence):
    """Render Agilent QQQ configuration."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input("Instrument Method", value=st.session_state.ms_method, placeholder="D:\\Methods\\method.m")
        st.session_state.ms_method = ms_method
    with col2:
        st.markdown('<div class="alert alert-info" style="margin-top:1.5rem;">📁 Data Folder from Step 1</div>', unsafe_allow_html=True)
    
    st.markdown("**Sample Table** — Position format: P1-A1 to P1-H12")
    
    if not sequence:
        st.markdown('<div class="alert alert-warning">⚠️ No samples configured. Go back to Step 2 to add samples.</div>', unsafe_allow_html=True)
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
    
    st.markdown('<div class="alert alert-info">💡 Double-click cells to edit • Fill Sample Position (e.g., P1-A1)</div>', unsafe_allow_html=True)
    
    edited_df = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, height=400, key='agilent_editor',
        column_config={
            "Sample Position": st.column_config.TextColumn("Sample Position", help="Format: P1-A1 to P1-H12"),
            "Sample Type": st.column_config.SelectboxColumn("Sample Type", options=AGILENT_SAMPLE_TYPES, required=True),
            "Injection Volume": st.column_config.SelectboxColumn("Injection Volume", options=AGILENT_INJ_OPTIONS, required=True)
        }
    )
    st.session_state.sequence_df = edited_df
    return edited_df


def render_hfx2_config(sequence):
    """Render HFX-2 configuration with full column format."""
    col1, col2 = st.columns(2)
    with col1:
        ms_method = st.text_input("Instrument Method (.meth)", value=st.session_state.ms_method, placeholder="D:\\Methods\\method.meth")
        st.session_state.ms_method = ms_method
        if ms_method and not ms_method.endswith('.meth'):
            st.markdown('<div class="alert alert-warning">⚠️ Should have .meth extension</div>', unsafe_allow_html=True)
    with col2:
        injection_volume = st.number_input("Injection Volume (µL)", min_value=0.01, max_value=100.0, value=st.session_state.injection_volume, step=0.1)
        st.session_state.injection_volume = injection_volume
    
    st.markdown("**Sample Table** — Position format: G:A1 to G:H12")
    
    if not sequence:
        st.markdown('<div class="alert alert-warning">⚠️ No samples configured. Go back to Step 2 to add samples.</div>', unsafe_allow_html=True)
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
            'Process Method': '',
            'Calibration File': '',
            'Position': '',
            'Inj Vol': injection_volume,
            'Level': 1 if needs_level else '',
            'Sample Wt': '',
            'Sample Vol': '',
            'ISTD Amt': '',
            'Dil Factor': 1,
            'L1 Study': '',
            'L2 Client': '',
            'L3 Laboratory': '',
            'L4 Company': '',
            'L5 Phone': '',
            'Comment': '',
            'Sample Name': sample_name  # This column is important!
        })
    
    df = pd.DataFrame(data)
    
    st.markdown('<div class="alert alert-info">💡 Double-click cells to edit • Fill Position (e.g., G:A1) • All columns included for HFX-2 format</div>', unsafe_allow_html=True)
    
    # Only show essential columns in editor, but keep all in dataframe
    display_columns = ['Sample Type', 'File Name', 'Sample ID', 'Path', 'Instrument Method', 'Position', 'Inj Vol', 'Dil Factor', 'Sample Name']
    
    edited_df = st.data_editor(
        df[display_columns], num_rows="dynamic", use_container_width=True, height=400, key='hfx_editor',
        column_config={
            "Sample Type": st.column_config.SelectboxColumn("Sample Type", options=HFX_SAMPLE_TYPES, required=True),
            "Position": st.column_config.TextColumn("Position", help="Format: G:A1 to G:H12"),
            "Inj Vol": st.column_config.NumberColumn("Inj Vol", min_value=0.01, format="%.2f"),
            "Dil Factor": st.column_config.NumberColumn("Dil Factor", min_value=1, default=1),
            "Sample Name": st.column_config.TextColumn("Sample Name", help="Sample name for reference")
        }
    )
    
    # Merge edited columns back into full dataframe
    for col in display_columns:
        if col in edited_df.columns:
            df[col] = edited_df[col].tolist() + [''] * (len(df) - len(edited_df)) if len(edited_df) < len(df) else edited_df[col].tolist()[:len(df)]
    
    # Handle added rows
    if len(edited_df) > len(df):
        for i in range(len(df), len(edited_df)):
            new_row = {col: '' for col in df.columns}
            for col in display_columns:
                if col in edited_df.columns:
                    new_row[col] = edited_df[col].iloc[i] if i < len(edited_df) else ''
            new_row['Dil Factor'] = 1
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    st.session_state.sequence_df = df
    return df


# ============================================================================
# STEP 5: EXPORT
# ============================================================================

def render_step5_export():
    """Render Step 5: Preview and Export."""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("""
        <div class="section-header">
            <div class="section-icon icon-cyan">📤</div>
            <span>Step 5: Preview & Export</span>
        </div>
    """, unsafe_allow_html=True)
    
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
        
        st.markdown('<div class="alert alert-success">✓ Ready to export!</div>', unsafe_allow_html=True)
    
    if st.button("← Back to Configuration", key='back_5'):
        st.session_state.step = 4
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_footer():
    """Render the app footer."""
    st.markdown("""
        <div class="footer">
            <strong>MS Batch Generator</strong> v2.0 · Built with Streamlit<br>
            Supports Sciex7500 · AgilentQQQ · HFX-2
        </div>
    """, unsafe_allow_html=True)

