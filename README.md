# MS Batch/Worklist Generator

A Streamlit web application for generating CSV batch files for mass spectrometry instruments (Sciex7500, AgilentQQQ, HFX-2).

## Features

- **Multi-instrument support**: Sciex7500, AgilentQQQ, HFX-2
- **Sample configuration**: Define standards, samples, QCs, and blanks with frequency rules
- **Flexible naming**: Auto-build names, manual entry, or import from CSV/Excel
- **Template system**: Save and load sample configurations
- **Validation**: Warnings for duplicate vial positions and missing QC/blanks
- **Editable tables**: Modify any value before export
- **CSV export**: With or without column headers

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage

### Step 1: Initial Setup
- Select your instrument (Sciex7500, AgilentQQQ, or HFX-2)
- Enter project name (format: MPG_25-12_GaIEMA)
- Specify the parent folder path for data files

### Step 2: Sample Configuration
- Toggle sample types (Standards, Samples, QCs, Blanks)
- Set counts for each type
- Configure frequency rules:
  - **At the start only**: Placed at the beginning
  - **At the end only**: Placed at the end
  - **At fixed interval**: Inserted every N samples

### Step 3: Naming Rules
- **None**: Auto-numbered (Sample1, QC1, etc.)
- **Auto-build**: Prefix_Index_Suffix format
- **Manual**: Enter each name individually
- **Import**: Load names from CSV/Excel file

### Step 4: Instrument Configuration
Configure instrument-specific settings:
- Method paths
- Plate types and positions
- Injection volumes
- Vial positions

### Step 5: Preview & Export
- Review the final table
- Download CSV (with or without headers)

## Template System

Save your sample configurations as templates for reuse:
1. Configure your sample types and naming rules
2. Click "Save as Template" in the sidebar
3. Load templates anytime from the dropdown

## File Structure

```
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── saved_templates.json # Saved user templates (auto-created)
└── README.md           # This file
```

## Notes

- AgilentQQQ requires data folder on D: drive
- HFX-2 method files must have .meth extension
- Duplicate vial positions will trigger warnings

