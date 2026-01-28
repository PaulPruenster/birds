import pandas as pd
from pathlib import Path
import traceback

def quick_validate():
    """Quick validation of exclusive birds"""
    base_path = Path("data")
    results_dir = Path("results_common_name")
    
    print("Starting validation...")
    print(f"Base path exists: {base_path.exists()}")
    print(f"Results dir exists: {results_dir.exists()}")
    
    # Load all exclusive lists
    exclusives = {}
    for forest in ["one", "two", "three"]:
        file_path = results_dir / f"{forest}_exclusive_birds.csv"
        print(f"Looking for {file_path}")
        if file_path.exists():
            df = pd.read_csv(file_path)
            if not df.empty and 'common_name' in df.columns:
                exclusives[forest] = set(df['common_name'])
                print(f"  Loaded {len(exclusives[forest])} exclusive birds for {forest}")
            else:
                print(f"  File empty or missing 'common_name' column: {file_path}")
        else:
            print(f"  File not found: {file_path}")
    
    print(f"\nLoaded exclusive birds for forests: {list(exclusives.keys())}")
    
    errors = []
    
    # Check each exclusive bird
    for forest, birds in exclusives.items():
        other_forests = [f for f in ["one", "two", "three"] if f != forest]
        print(f"\nChecking exclusive birds for forest '{forest}'...")
        print(f"  Has {len(birds)} birds to check")
        
        for other_forest in other_forests:
            other_path = base_path / other_forest
            print(f"  Checking against folder: {other_path}")
            
            if other_path.exists():
                excel_files = list(other_path.glob("*.xlsx"))
                print(f"    Found {len(excel_files)} Excel files")
                
                for excel_file in excel_files:
                    print(f"    Processing: {excel_file.name}")
                    try:
                        df = pd.read_excel(excel_file, sheet_name='Beobachtungen')
                        print(f"      Successfully read Excel file")
                        
                        if 'common_name' in df.columns and 'confidence' in df.columns:
                            df_filtered = df[df['confidence'] > 0.8]
                            print(f"      Found {len(df_filtered)} rows with confidence > 0.8")
                            
                            other_birds = set(df_filtered['common_name'].dropna().astype(str).str.strip())
                            print(f"      Found {len(other_birds)} unique birds in this file")
                            
                            # Check for overlap
                            overlapping = birds.intersection(other_birds)
                            if overlapping:
                                print(f"      Found {len(overlapping)} overlapping birds!")
                                for bird in overlapping:
                                    error = f"'{bird}' (exclusive to {forest}) found in {other_forest}/{excel_file.name}"
                                    print(error)
                                    errors.append(error)
                        else:
                            print(f"      Missing required columns in {excel_file.name}")
                            
                    except Exception as e:
                        print(f"      ERROR reading {excel_file.name}: {str(e)}")
                        traceback.print_exc()  # This will show the full error trace
            else:
                print(f"    Folder does not exist: {other_path}")
    
    # Print results
    print("\n" + "="*50)
    print("VALIDATION RESULTS")
    print("="*50)
    
    if errors:
        print(f"\n❌ Found {len(errors)} errors:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ All exclusive birds validated successfully!")
    
    return not errors

if __name__ == "__main__":
    quick_validate()