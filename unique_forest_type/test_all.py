import pandas as pd
from pathlib import Path

def validate_common_to_all():
    """Validate that birds marked as common to all forests actually appear in all"""
    base_path = Path("data")
    results_dir = Path("results_common_name")
    
    print("=" * 60)
    print("VALIDATING BIRDS COMMON TO ALL FORESTS")
    print("=" * 60)
    
    # Load the common birds list
    common_file = results_dir / "common_to_all_forests.csv"
    
    if not common_file.exists():
        print(f"❌ Common birds file not found: {common_file}")
        return False
    
    df_common = pd.read_csv(common_file)
    
    if 'common_name' not in df_common.columns:
        print("❌ 'common_name' column not found in common birds file")
        return False
    
    if df_common.empty:
        print("ℹ️ Common birds list is empty")
        return True
    
    common_birds = set(df_common['common_name'].astype(str).str.strip())
    print(f"\nLoaded {len(common_birds)} birds that should be in all forests:")
    for i, bird in enumerate(sorted(common_birds), 1):
        print(f"  {i:2}. {bird}")
    
    # Track where each bird is found
    bird_status = {bird: [] for bird in common_birds}
    
    print("\n" + "-" * 60)
    print("CHECKING EACH FOREST FOLDER:")
    print("-" * 60)
    
    # Check each forest folder
    for forest in ["one", "two", "three"]:
        folder_path = base_path / forest
        print(f"\nChecking forest '{forest}' at: {folder_path}")
        
        if not folder_path.exists():
            print(f"  ❌ Folder does not exist!")
            continue
        
        # Get all Excel files
        excel_files = list(folder_path.glob("*.xlsx"))
        print(f"  Found {len(excel_files)} Excel files")
        
        forest_birds = set()
        
        # Process each file
        for i, excel_file in enumerate(excel_files, 1):
            print(f"  File {i}/{len(excel_files)}: {excel_file.name}")
            
            try:
                # Read the file
                df = pd.read_excel(excel_file, sheet_name='Beobachtungen')
                
                # Filter by confidence
                if 'confidence' in df.columns:
                    df = df[df['confidence'] > 0.8]
                
                # Extract bird names
                if 'common_name' in df.columns:
                    df['common_name'] = df['common_name'].astype(str).str.strip()
                    file_birds = set(df['common_name'].dropna().unique())
                    forest_birds.update(file_birds)
                    
                    # Show matching birds from our list
                    matching = file_birds.intersection(common_birds)
                    if matching:
                        print(f"    Found {len(matching)} common birds in this file:")
                        for bird in sorted(matching):
                            print(f"      ✓ {bird}")
                else:
                    print(f"    ⚠ No 'common_name' column found")
                    
            except Exception as e:
                print(f"    ⚠ Could not read file: {str(e)[:50]}...")
        
        print(f"  Total unique birds in forest '{forest}': {len(forest_birds)}")
        
        # Check which common birds are in this forest
        found_here = forest_birds.intersection(common_birds)
        missing_here = common_birds - forest_birds
        
        print(f"  Common birds found in '{forest}': {len(found_here)}")
        print(f"  Common birds missing in '{forest}': {len(missing_here)}")
        
        # Update status for each bird
        for bird in common_birds:
            if bird in found_here:
                bird_status[bird].append(forest)
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    # Check which birds are missing from which forests
    errors = []
    for bird, found_in in bird_status.items():
        missing_in = [f for f in ["one", "two", "three"] if f not in found_in]
        if missing_in:
            errors.append({
                'bird': bird,
                'found_in': found_in,
                'missing_in': missing_in
            })
    
    if errors:
        print(f"\n❌ Found {len(errors)} errors:")
        print("-" * 40)
        
        for error in errors:
            print(f"\n'{error['bird']}':")
            print(f"  Found in:    {sorted(error['found_in'])}")
            print(f"  Missing in:  {sorted(error['missing_in'])}")
            
            # Show details about missing folders
            for missing_forest in error['missing_in']:
                missing_path = base_path / missing_forest
                print(f"\n  Looking in folder '{missing_forest}':")
                
                if missing_path.exists():
                    excel_files = list(missing_path.glob("*.xlsx"))
                    print(f"    Has {len(excel_files)} Excel files")
                    
                    # Quick check of each file for this bird
                    for excel_file in excel_files[:3]:  # Check first 3 files
                        try:
                            df = pd.read_excel(excel_file, sheet_name='Beobachtungen')
                            if 'common_name' in df.columns:
                                bird_names = set(df['common_name'].astype(str).str.strip())
                                if error['bird'] in bird_names:
                                    print(f"    Found in {excel_file.name} but confidence might be ≤ 0.8")
                        except:
                            pass
                else:
                    print(f"    Folder doesn't exist!")
    else:
        print("\n✅ All birds are correctly found in all three forests!")
    
    # Summary
    print("\n" + "-" * 60)
    print("SUMMARY")
    print("-" * 60)
    print(f"Total birds checked: {len(common_birds)}")
    print(f"Correctly in all forests: {len(common_birds) - len(errors)}")
    print(f"Missing from some forests: {len(errors)}")
    
    return len(errors) == 0

if __name__ == "__main__":
    validate_common_to_all()