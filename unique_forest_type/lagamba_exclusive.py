import pandas as pd
from pathlib import Path

# Read species list
species_df = pd.read_csv('LaGamba2026ChirpityBirdNETspecies_list.csv')
species_df.columns = species_df.columns.str.strip()

# Initialize results
result = {}
for _, row in species_df.iterrows():
    sci_name = row.get('scientific_name')
    common_name = row.get('common_name', '')
    if sci_name:
        result[sci_name] = {
            'common_name': common_name,
            'one': 0, 'two': 0, 'three': 0
        }

# Process forest folders
forest_folders = ['one', 'two', 'three']
for forest in forest_folders:
    folder = Path('data') / forest
    if not folder.exists():
        continue
        
    for excel_file in folder.glob('*.xlsx'):
        try:
            xl = pd.ExcelFile(excel_file)
            if 'HaeufigeArten_conf>0.8' in xl.sheet_names:
                df = pd.read_excel(excel_file, sheet_name='HaeufigeArten_conf>0.8')
                df.columns = df.columns.str.strip()
                
                # Ensure column names match
                if 'scientific_name' not in df.columns:
                    for col in df.columns:
                        if 'scientific' in col.lower() or 'species' in col.lower():
                            df = df.rename(columns={col: 'scientific_name'})
                            break
                
                if 'n' not in df.columns:
                    for col in df.columns:
                        if col.lower() in ['n', 'count', 'occurrences']:
                            df = df.rename(columns={col: 'n'})
                            break
                
                # Update counts
                for _, row in df.iterrows():
                    sci_name = row.get('scientific_name')
                    if sci_name in result:
                        result[sci_name][forest] += row.get('n', 0)
                        
        except Exception:
            continue

# Create output DataFrame
output = []
for sci_name, data in result.items():
    row = {
        'scientific_name': sci_name,
        'common_name': data['common_name'],
        'one': data['one'],
        'two': data['two'],
        'three': data['three'],
        'total_n': data['one'] + data['two'] + data['three']
    }
    output.append(row)

output_df = pd.DataFrame(output).sort_values('scientific_name')
output_df.to_csv('forest_bird_occurrences.csv', index=False)