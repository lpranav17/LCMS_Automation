"""
Step 2: Sample Configuration
"""

import streamlit as st
from streamlit_sortables import sort_items
from config import FREQUENCY_RULES
from utils import generate_sequence


def render_step2_sample_config():
    """Render Step 2: Sample Types Configuration."""
    st.subheader("🧫 Step 2: Sample Configuration")
    
    # Initialize order if not present, or migrate old order to new default
    if 'sample_type_order' not in st.session_state:
        st.session_state.sample_type_order = ['blanks', 'qc', 'standards', 'samples']
    else:
        # Migrate old default order to new default order
        old_default = ['standards', 'samples', 'qc', 'blanks']
        current_order = st.session_state.sample_type_order
        if current_order == old_default:
            st.session_state.sample_type_order = ['blanks', 'qc', 'standards', 'samples']
    
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
    # Set default order when all types are enabled
    all_types = ['blanks', 'qc', 'standards', 'samples']
    all_enabled = all(st.session_state.sample_types[t]['enabled'] for t in all_types)
    
    if all_enabled:
        # When all types are enabled, ensure default order is set
        # Only reset if the enabled types don't match the default order
        enabled_types = [t for t in st.session_state.sample_type_order if st.session_state.sample_types[t]['enabled']]
        if set(enabled_types) == set(all_types) and enabled_types != all_types:
            # Reset to default order: blanks, QC, standards, samples
            st.session_state.sample_type_order = all_types.copy()
            enabled_types = all_types.copy()
    else:
        enabled_types = [t for t in st.session_state.sample_type_order if st.session_state.sample_types[t]['enabled']]
    
    if len(enabled_types) > 1:
        st.markdown("---")
        st.markdown("""
            <div style="color: #ffffff; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">
                🔀 <strong>Sequence Order</strong> <em style="color: #94a3b8; font-weight: 400;">(drag to reorder)</em>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)  # Spacer
        
        # Simple text labels
        key_to_label = {
            'standards': 'Standards', 
            'samples': 'Samples', 
            'qc': 'QC', 
            'blanks': 'Blanks'
        }
        label_to_key = {v: k for k, v in key_to_label.items()}
        
        # Get current order as labels
        current_labels = [key_to_label[k] for k in enabled_types]
        
        # Drag and drop sortable with container - add custom styling wrapper
        st.markdown("""
            <div style="background: #1e293b; border: 2px solid #3b82f6; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
        """, unsafe_allow_html=True)
        
        # Drag and drop sortable with container
        with st.container():
            sorted_labels = sort_items(current_labels, direction="horizontal")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)  # Spacer
        
        # Convert back to keys
        sorted_enabled = [label_to_key[label] for label in sorted_labels]
        
        # Update session state
        disabled_types = [t for t in st.session_state.sample_type_order if not st.session_state.sample_types[t]['enabled']]
        st.session_state.sample_type_order = sorted_enabled + disabled_types
        
        # Show order preview
        st.success(f"**Run order:** {' → '.join(sorted_labels)}")
    
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
                if current_rule in ['At fixed interval', 'At start + fixed interval', 'At start + fixed interval + at end']:
                    interval = st.number_input("Every N samples", min_value=1, max_value=100, value=config.get('interval', 5), key=f"interval_{type_name}")
                    st.session_state.sample_types[type_name]['interval'] = interval
            
            # Start count for "At start + fixed interval" and "At start + fixed interval + at end"
            if current_rule in ['At start + fixed interval', 'At start + fixed interval + at end'] and count > 0:
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

