import pandas as pd
from pathlib import Path

bird_name = input("Bird to search: ").strip()

for forest in ["one", "two", "three"]:
    print(f"\n{forest}:")
    folder = Path("data") / forest
    
    for file in sorted(folder.glob("*.xlsx")):
        try:
            df = pd.read_excel(file, sheet_name='Beobachtungen')
            if 'confidence' in df.columns:
                df = df[df['confidence'] > 0.8]
            
            if 'common_name' in df.columns:
                df['common_name'] = df['common_name'].astype(str).str.strip()
                match = df[df['common_name'] == bird_name]
                
                if not match.empty:
                    row = match.index[0] + 2
                    print(f"  {file.name} (row {row})")
                    break
        except:
            pass