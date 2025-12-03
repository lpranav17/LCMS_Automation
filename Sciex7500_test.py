import pandas as pd
from datetime import datetime

# Test Scenario 1: Basic sequence with all sample types
def generate_basic_test():
    """Generate a basic test sequence with standards, samples, QCs, and blanks"""
    data = {
        'Sample Name': [],
        'MS Method': [],
        'LC Method': [],
        'Rack Type': [],
        'Plate Type': [],
        'Plate Number': [],
        'Vial Number': [],
        'Injection Volume (uL)': [],
        'Data File': []
    }
    
    # Configuration
    project_name = "MPG_25-12_TestRun"
    folder_path = "D:/LCMS_Data/Test_Project"
    ms_method = "D:/Methods/Sciex/standard_method.dam"
    lc_method = "D:/Methods/Sciex/gradient_30min.lcm"
    plate_type = "MTP 96"
    plate_number = 1
    injection_vol = 5.0
    
    vial_counter = 1
    
    # Add 5 Standards at the start
    for i in range(1, 6):
        data['Sample Name'].append(f'Std_{i}_50uM')
        data['MS Method'].append(ms_method)
        data['LC Method'].append(lc_method)
        data['Rack Type'].append('SIL-40 Drawer')
        data['Plate Type'].append(plate_type)
        data['Plate Number'].append(plate_number)
        data['Vial Number'].append(vial_counter)
        data['Injection Volume (uL)'].append(injection_vol)
        data['Data File'].append(f'{folder_path}/Std_{i}_50uM')
        vial_counter += 1
    
    # Add blank at position 6
    data['Sample Name'].append('Blank_1')
    data['MS Method'].append(ms_method)
    data['LC Method'].append(lc_method)
    data['Rack Type'].append('SIL-40 Drawer')
    data['Plate Type'].append(plate_type)
    data['Plate Number'].append(plate_number)
    data['Vial Number'].append(vial_counter)
    data['Injection Volume (uL)'].append(injection_vol)
    data['Data File'].append(f'{folder_path}/Blank_1')
    vial_counter += 1
    
    # Add 15 Samples with blanks every 5 samples
    for i in range(1, 16):
        data['Sample Name'].append(f'Sample_dil_5_{i}')
        data['MS Method'].append(ms_method)
        data['LC Method'].append(lc_method)
        data['Rack Type'].append('SIL-40 Drawer')
        data['Plate Type'].append(plate_type)
        data['Plate Number'].append(plate_number)
        data['Vial Number'].append(vial_counter)
        data['Injection Volume (uL)'].append(injection_vol)
        data['Data File'].append(f'{folder_path}/Sample_dil_5_{i}')
        vial_counter += 1
        
        # Add blank every 5 samples
        if i % 5 == 0:
            data['Sample Name'].append(f'Blank_{i//5 + 1}')
            data['MS Method'].append(ms_method)
            data['LC Method'].append(lc_method)
            data['Rack Type'].append('SIL-40 Drawer')
            data['Plate Type'].append(plate_type)
            data['Plate Number'].append(plate_number)
            data['Vial Number'].append(vial_counter)
            data['Injection Volume (uL)'].append(injection_vol)
            data['Data File'].append(f'{folder_path}/Blank_{i//5 + 1}')
            vial_counter += 1
    
    # Add 2 QCs
    for i in range(1, 3):
        data['Sample Name'].append(f'QC_matrix_{i}')
        data['MS Method'].append(ms_method)
        data['LC Method'].append(lc_method)
        data['Rack Type'].append('SIL-40 Drawer')
        data['Plate Type'].append(plate_type)
        data['Plate Number'].append(plate_number)
        data['Vial Number'].append(vial_counter)
        data['Injection Volume (uL)'].append(injection_vol)
        data['Data File'].append(f'{folder_path}/QC_matrix_{i}')
        vial_counter += 1
    
    return pd.DataFrame(data)


# Test Scenario 2: 54-vial plate test
def generate_vial_plate_test():
    """Generate test with 1.5mL VT54 plate"""
    data = {
        'Sample Name': [],
        'MS Method': [],
        'LC Method': [],
        'Rack Type': [],
        'Plate Type': [],
        'Plate Number': [],
        'Vial Number': [],
        'Injection Volume (uL)': [],
        'Data File': []
    }
    
    project_name = "TEST_VT54_Plate"
    folder_path = "D:/LCMS_Data/VT54_Test"
    ms_method = "D:/Methods/Sciex/quick_scan.dam"
    lc_method = "D:/Methods/Sciex/isocratic_10min.lcm"
    plate_type = "1.5mL VT54 (54 vial)"
    
    # Add 20 samples
    for i in range(1, 21):
        data['Sample Name'].append(f'Plasma_{i}_1to10')
        data['MS Method'].append(ms_method)
        data['LC Method'].append(lc_method)
        data['Rack Type'].append('SIL-40 Drawer')
        data['Plate Type'].append(plate_type)
        data['Plate Number'].append(1)
        data['Vial Number'].append(i)
        data['Injection Volume (uL)'].append(10.0)
        data['Data File'].append(f'{folder_path}/Plasma_{i}_1to10')
    
    return pd.DataFrame(data)


# Test Scenario 3: Multi-plate sequence
def generate_multiplate_test():
    """Generate test spanning multiple plates"""
    data = {
        'Sample Name': [],
        'MS Method': [],
        'LC Method': [],
        'Rack Type': [],
        'Plate Type': [],
        'Plate Number': [],
        'Vial Number': [],
        'Injection Volume (uL)': [],
        'Data File': []
    }
    
    folder_path = "D:/LCMS_Data/Multiplate_Test"
    ms_method = "D:/Methods/Sciex/sensitivity_method.dam"
    lc_method = "D:/Methods/Sciex/gradient_45min.lcm"
    
    # Plate 1: Standards and QCs
    for i in range(1, 11):
        data['Sample Name'].append(f'Std_cal_{i}')
        data['MS Method'].append(ms_method)
        data['LC Method'].append(lc_method)
        data['Rack Type'].append('SIL-40 Drawer')
        data['Plate Type'].append('MTP 96')
        data['Plate Number'].append(1)
        data['Vial Number'].append(i)
        data['Injection Volume (uL)'].append(2.0)
        data['Data File'].append(f'{folder_path}/Std_cal_{i}')
    
    # Plate 2: Samples
    for i in range(1, 50):
        data['Sample Name'].append(f'Serum_sample_{i}')
        data['MS Method'].append(ms_method)
        data['LC Method'].append(lc_method)
        data['Rack Type'].append('SIL-40 Drawer')
        data['Plate Type'].append('MTP 96')
        data['Plate Number'].append(2)
        data['Vial Number'].append(i)
        data['Injection Volume (uL)'].append(5.0)
        data['Data File'].append(f'{folder_path}/Serum_sample_{i}')
    
    # Plate 3: More samples
    for i in range(1, 30):
        data['Sample Name'].append(f'Urine_sample_{i}')
        data['MS Method'].append(ms_method)
        data['LC Method'].append(lc_method)
        data['Rack Type'].append('SIL-40 Drawer')
        data['Plate Type'].append('MTP 96')
        data['Plate Number'].append(3)
        data['Vial Number'].append(i)
        data['Injection Volume (uL)'].append(5.0)
        data['Data File'].append(f'{folder_path}/Urine_sample_{i}')
    
    return pd.DataFrame(data)


# Generate all test files
print("Generating Sciex7500 test data files...")

# Test 1: Basic sequence
df1 = generate_basic_test()
df1.to_excel('Sciex7500_Test1_Basic.xlsx', index=False)
df1.to_csv('Sciex7500_Test1_Basic.csv', index=False)
print(f"✓ Test 1 generated: {len(df1)} samples (Basic sequence with all sample types)")

# Test 2: VT54 plate
df2 = generate_vial_plate_test()
df2.to_excel('Sciex7500_Test2_VT54.xlsx', index=False)
df2.to_csv('Sciex7500_Test2_VT54.csv', index=False)
print(f"✓ Test 2 generated: {len(df2)} samples (1.5mL VT54 plate test)")

# Test 3: Multi-plate
df3 = generate_multiplate_test()
df3.to_excel('Sciex7500_Test3_Multiplate.xlsx', index=False)
df3.to_csv('Sciex7500_Test3_Multiplate.csv', index=False)
print(f"✓ Test 3 generated: {len(df3)} samples (Multi-plate sequence)")

print("\n" + "="*60)
print("FILES GENERATED SUCCESSFULLY!")
print("="*60)
print("\nYou now have 6 files:")
print("  • Sciex7500_Test1_Basic.xlsx/csv")
print("  • Sciex7500_Test2_VT54.xlsx/csv")
print("  • Sciex7500_Test3_Multiplate.xlsx/csv")