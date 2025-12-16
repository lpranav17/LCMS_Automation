"""
CSS styles for MS Batch Generator - Clean Dark Theme
"""

def get_dark_theme_css():
    """Return clean, professional dark theme CSS styles."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Base styles */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #e2e8f0 !important;
        }
        
        .stApp { background: #0f172a !important; }
        
        #MainMenu, footer, header { visibility: hidden; }
        
        /* Universal text color */
        .stApp p, .stApp span, .stApp label, .stApp div,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stMarkdown, .stMarkdown *, .element-container *,
        [data-testid] p, [data-testid] span, [data-testid] label {
            color: #e2e8f0 !important;
        }
        
        /* Widget labels */
        [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
        .stSelectbox label, .stTextInput label, .stNumberInput label,
        .stCheckbox label, .stRadio label, .stToggle label,
        .stFileUploader label, .stMultiSelect label {
            color: #e2e8f0 !important;
            font-weight: 500 !important;
        }
        
        /* Inputs */
        .stTextInput input, .stNumberInput input,
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            color: #e2e8f0 !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25) !important;
        }
        
        .stTextInput input::placeholder, .stNumberInput input::placeholder {
            color: #64748b !important;
        }
        
        /* Number input +/- buttons */
        .stNumberInput button {
            background: #334155 !important;
            border: 1px solid #475569 !important;
            color: #e2e8f0 !important;
        }
        
        .stNumberInput button:hover {
            background: #475569 !important;
            border-color: #3b82f6 !important;
        }
        
        .stNumberInput button svg {
            fill: #e2e8f0 !important;
            stroke: #e2e8f0 !important;
        }
        
        /* Step buttons in number input */
        .stNumberInput [data-testid="stNumberInputStepUp"],
        .stNumberInput [data-testid="stNumberInputStepDown"] {
            background: #334155 !important;
            color: #e2e8f0 !important;
        }
        
        /* Selectbox */
        .stSelectbox > div > div,
        .stSelectbox [data-baseweb="select"],
        .stSelectbox [data-baseweb="select"] > div {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [data-baseweb="select"] div,
        .stSelectbox [data-baseweb="select"] input {
            color: #e2e8f0 !important;
        }
        
        /* Dropdown */
        [data-baseweb="popover"], [data-baseweb="menu"],
        [data-baseweb="popover"] *, [data-baseweb="menu"] * {
            background: #1e293b !important;
            color: #e2e8f0 !important;
        }
        
        [data-baseweb="menu"] li:hover { background: #334155 !important; }
        [data-baseweb="tag"] { background: #334155 !important; color: #e2e8f0 !important; }
        
        /* Sidebar - always visible, cannot be collapsed */
        section[data-testid="stSidebar"] { 
            background: #1e293b !important;
            transform: none !important;
            min-width: 300px !important;
        }
        section[data-testid="stSidebar"] > div { background: transparent !important; }
        section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
        
        /* Hide the sidebar close button so users can't collapse it */
        section[data-testid="stSidebar"] button[data-testid="baseButton-headerNoPadding"],
        button[data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        
        /* Force sidebar to always be expanded */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(0) !important;
            width: 300px !important;
            min-width: 300px !important;
        }
        
        /* Expanders */
        div[data-testid="stExpander"] {
            background: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] * { color: #e2e8f0 !important; }
        div[data-testid="stExpander"] > div:first-child { background: #1e293b !important; }
        
        /* Buttons - All types */
        .stButton > button,
        [data-testid="baseButton-secondary"] {
            background: #334155 !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
            color: #e2e8f0 !important;
            font-weight: 500 !important;
        }
        
        .stButton > button:hover,
        [data-testid="baseButton-secondary"]:hover {
            background: #475569 !important;
            border-color: #3b82f6 !important;
        }
        
        /* Disabled buttons */
        .stButton > button:disabled,
        [data-testid="baseButton-secondary"]:disabled {
            background: #1e293b !important;
            border-color: #334155 !important;
            color: #64748b !important;
            opacity: 0.6 !important;
        }
        
        .stButton > button[kind="primary"],
        [data-testid="baseButton-primary"] {
            background: #3b82f6 !important;
            border-color: #3b82f6 !important;
            color: #ffffff !important;
        }
        
        .stDownloadButton > button {
            background: #10b981 !important;
            border: none !important;
            color: #ffffff !important;
        }
        
        /* Toggles & Checkboxes */
        .stToggle label span, .stCheckbox label span, .stRadio label span {
            color: #e2e8f0 !important;
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] section {
            background: #1e293b !important;
            border: 2px dashed #334155 !important;
            border-radius: 8px !important;
        }
        
        /* Data tables / Data editor */
        .stDataFrame, [data-testid="stDataFrame"],
        [data-testid="stDataEditor"], .stDataEditor {
            background: #1e293b !important;
        }
        
        [data-testid="stDataFrame"] *, [data-testid="stDataEditor"] *,
        .stDataFrame *, .stDataEditor * {
            color: #e2e8f0 !important;
        }
        
        /* Data editor cells */
        [data-testid="stDataEditor"] [role="gridcell"],
        [data-testid="stDataEditor"] [role="columnheader"] {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        
        [data-testid="stDataEditor"] [role="columnheader"] {
            background: #0f172a !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stDataEditor"] [role="gridcell"]:hover {
            background: #334155 !important;
        }
        
        /* Data editor input */
        [data-testid="stDataEditor"] input {
            background: #1e293b !important;
            color: #e2e8f0 !important;
            border: 1px solid #3b82f6 !important;
        }
        
        /* Data editor add row button */
        [data-testid="stDataEditor"] button {
            background: #334155 !important;
            color: #e2e8f0 !important;
            border: 1px solid #475569 !important;
        }
        
        [data-testid="stDataEditor"] button:hover {
            background: #475569 !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] { color: #3b82f6 !important; }
        [data-testid="stMetricLabel"] { color: #94a3b8 !important; }
        
        /* Custom components */
        .main-header-accent {
            font-size: 2rem;
            font-weight: 700;
            color: #3b82f6 !important;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: #94a3b8 !important;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        
        .section-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.1rem;
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid #334155;
        }
        
        .section-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .icon-blue { background: #3b82f6; }
        .icon-green { background: #10b981; }
        .icon-amber { background: #f59e0b; }
        .icon-purple { background: #8b5cf6; }
        .icon-cyan { background: #06b6d4; }
        
        /* Sidebar */
        .sidebar-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #334155;
            margin-bottom: 1rem;
        }
        
        .sidebar-logo {
            width: 36px;
            height: 36px;
            background: #3b82f6;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .sidebar-title { font-weight: 600; color: #e2e8f0; }
        .sidebar-subtitle { font-size: 0.75rem; color: #94a3b8; }
        
        /* Steps */
        .stepper-container { display: flex; flex-direction: column; gap: 0.25rem; }
        
        .step-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 0.875rem;
            color: #94a3b8;
        }
        
        .step-item.active {
            background: rgba(59, 130, 246, 0.15);
            color: #3b82f6;
            font-weight: 500;
        }
        
        .step-item.completed { color: #10b981; }
        
        .step-number {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 600;
            background: #334155;
            color: #94a3b8;
        }
        
        .step-item.active .step-number { background: #3b82f6; color: white; }
        .step-item.completed .step-number { background: #10b981; color: white; }
        
        /* Alerts */
        .alert {
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.75rem 0;
            font-size: 0.875rem;
        }
        
        .alert-info { background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); color: #60a5fa; }
        .alert-warning { background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); color: #fbbf24; }
        .alert-success { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399; }
        .alert-error { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; }
        
        /* Badges */
        .instrument-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.375rem 0.75rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-bottom: 1rem;
        }
        
        .badge-sciex { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-agilent { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
        .badge-hfx { background: rgba(139, 92, 246, 0.15); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.3); }
        
        .code-preview {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            font-family: monospace;
            font-size: 0.8rem;
            color: #60a5fa;
        }
        
        .template-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }
        
        .footer {
            text-align: center;
            padding: 1.5rem 0;
            color: #64748b;
            font-size: 0.8rem;
            border-top: 1px solid #334155;
            margin-top: 2rem;
        }
        
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
        
        /* Streamlit sortables - fix overflow and sizing */
        [data-testid="stCustomComponentV1"] {
            background: transparent !important;
            overflow: visible !important;
            min-height: 70px !important;
        }
        
        [data-testid="stCustomComponentV1"] iframe {
            background: transparent !important;
            border: none !important;
            min-height: 70px !important;
            height: auto !important;
            overflow: visible !important;
        }
        
        /* Fix element container overflow */
        .element-container:has([data-testid="stCustomComponentV1"]) {
            overflow: visible !important;
            min-height: 70px !important;
        }
        
        /* Ensure the sortables wrapper doesn't clip content */
        .stCustomComponentV1, div:has(> iframe) {
            overflow: visible !important;
        }
    </style>
    """

