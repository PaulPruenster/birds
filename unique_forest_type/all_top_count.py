import pandas as pd
from pathlib import Path

# Initialize dictionary to store results
result = {}

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
                
                # Try to find common_name column
                if 'common_name' not in df.columns:
                    for col in df.columns:
                        if 'common' in col.lower() or 'name' in col.lower() and col != 'scientific_name':
                            df = df.rename(columns={col: 'common_name'})
                            break
                    else:
                        # If no common_name column found, create empty one
                        df['common_name'] = ''
                
                if 'n' not in df.columns:
                    for col in df.columns:
                        if col.lower() in ['n', 'count', 'occurrences', 'detections']:
                            df = df.rename(columns={col: 'n'})
                            break
                
                # Update counts
                for _, row in df.iterrows():
                    sci_name = row.get('scientific_name')
                    if pd.isna(sci_name):
                        continue
                    
                    # Convert to string and strip whitespace
                    sci_name = str(sci_name).strip()
                    
                    if sci_name not in result:
                        result[sci_name] = {
                            'common_name': row.get('common_name', ''),
                            'one': 0, 'two': 0, 'three': 0
                        }
                    
                    # Add count to the specific forest
                    result[sci_name][forest] += int(row.get('n', 0))
                        
        except Exception as e:
            print(f"Error processing {excel_file}: {e}")
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
output_df.to_csv('all_birds_forest_occurrences.csv', index=False)

print(f"Processed {len(output_df)} unique bird species")
print(f"Output saved to 'all_birds_forest_occurrences.csv'")