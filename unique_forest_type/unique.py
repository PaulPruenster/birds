import pandas as pd
import os
from pathlib import Path
from collections import defaultdict

def process_forest_data():
    # Define paths
    base_path = Path("data")
    forest_folders = ["one", "two", "three"]
    
    # Dictionary to store birds for each forest type
    forest_birds = defaultdict(set)
    
    print("Processing Excel files...")
    print("-" * 50)
    
    # Process each forest folder
    for forest in forest_folders:
        folder_path = base_path / forest
        print(f"\nProcessing folder: {forest}")
        
        if not folder_path.exists():
            print(f"  Warning: Folder '{folder_path}' does not exist. Skipping.")
            continue
        
        # Find all Excel files in the folder
        excel_files = list(folder_path.glob("*.xlsx"))
        print(f"  Found {len(excel_files)} Excel files")
        
        all_observations = []
        
        # Read each Excel file
        for excel_file in excel_files:
            try:
                # Read the specific sheet 'Beobachtungen'
                df = pd.read_excel(excel_file, sheet_name='Beobachtungen')
                
                # Apply confidence filter
                df_filtered = df[df['confidence'] > 0.8]
                
                if not df_filtered.empty:
                    all_observations.append(df_filtered)
                    print(f"    {excel_file.name}: {len(df_filtered)} records after filtering")
                else:
                    print(f"    {excel_file.name}: No records with confidence > 0.8")
                    
            except FileNotFoundError:
                print(f"    Error: File {excel_file.name} not found")
            except ValueError as e:
                if "Worksheet named" in str(e) and "not found" in str(e):
                    print(f"    Error: Sheet 'Beobachtungen' not found in {excel_file.name}")
                else:
                    print(f"    Error reading {excel_file.name}: {e}")
            except Exception as e:
                print(f"    Error reading {excel_file.name}: {e}")
        
        # Combine all observations for this forest
        if all_observations:
            combined_df = pd.concat(all_observations, ignore_index=True)
            
            # Get unique scientific names
            if 'scientific_name' in combined_df.columns:
                unique_birds = set(combined_df['scientific_name'].dropna().unique())
                forest_birds[forest] = unique_birds
                print(f"  Total unique birds in {forest}: {len(unique_birds)}")
            else:
                print(f"  Warning: 'scientific_name' column not found in {forest}")
                forest_birds[forest] = set()
        else:
            print(f"  No valid observations found in {forest}")
            forest_birds[forest] = set()
    
    return forest_birds

def analyze_and_save_results(forest_birds):
    """Analyze the data and save results to CSV files"""
    
    # Create output directory
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    # Check which forests have data
    valid_forests = [f for f in forest_birds.keys() if forest_birds[f]]
    
    if len(valid_forests) < 3:
        print(f"\nWarning: Only found data from {len(valid_forests)} forest(s): {valid_forests}")
    
    # 1. Save unique birds for each forest
    print("\n1. SAVING UNIQUE BIRDS FOR EACH FOREST:")
    print("-" * 40)
    
    for forest in ['one', 'two', 'three']:
        if forest in forest_birds:
            birds = forest_birds[forest]
            if birds:
                # Convert to DataFrame and save
                df = pd.DataFrame(sorted(birds), columns=['scientific_name'])
                output_file = output_dir / f"{forest}_unique_birds.csv"
                df.to_csv(output_file, index=False)
                print(f"{forest.upper()}: Saved {len(birds)} birds to {output_file}")
            else:
                print(f"{forest.upper()}: No birds found (empty CSV will be created)")
                # Create empty CSV
                df = pd.DataFrame(columns=['scientific_name'])
                output_file = output_dir / f"{forest}_unique_birds.csv"
                df.to_csv(output_file, index=False)
    
    # 2. Find birds unique to each forest type (only in that forest)
    print("\n\n2. BIRDS UNIQUE TO EACH FOREST TYPE:")
    print("   (Birds found in only one specific forest)")
    print("-" * 40)
    
    # Save unique-to-each-forest birds
    for forest in valid_forests:
        other_forests = [f for f in valid_forests if f != forest]
        
        if other_forests:
            # Birds in this forest but not in any other
            birds_in_this_forest = forest_birds[forest]
            birds_in_other_forests = set().union(*[forest_birds[f] for f in other_forests])
            unique_birds = birds_in_this_forest - birds_in_other_forests
            
            if unique_birds:
                df = pd.DataFrame(sorted(unique_birds), columns=['scientific_name'])
                output_file = output_dir / f"{forest}_exclusive_birds.csv"
                df.to_csv(output_file, index=False)
                print(f"\n{forest.upper()} (exclusive: {len(unique_birds)}):")
                print(f"  Saved to: {output_file}")
                # Show first 5 birds
                for bird in sorted(unique_birds)[:5]:
                    print(f"  - {bird}")
                if len(unique_birds) > 5:
                    print(f"  ... and {len(unique_birds) - 5} more")
            else:
                print(f"\n{forest.upper()}: No exclusive birds")
                # Create empty CSV
                df = pd.DataFrame(columns=['scientific_name'])
                output_file = output_dir / f"{forest}_exclusive_birds.csv"
                df.to_csv(output_file, index=False)
    
    # 3. Find birds common to all forests
    print("\n\n3. BIRDS COMMON TO ALL FORESTS:")
    print("-" * 40)
    
    if len(valid_forests) >= 3:
        # Find intersection of all three forests
        common_birds = (forest_birds['one'] & 
                       forest_birds['two'] & 
                       forest_birds['three'])
        
        if common_birds:
            df = pd.DataFrame(sorted(common_birds), columns=['scientific_name'])
            output_file = output_dir / "common_to_all_forests.csv"
            df.to_csv(output_file, index=False)
            
            print(f"\nFound {len(common_birds)} bird(s) in all 3 forests:")
            print(f"Saved to: {output_file}")
            for bird in sorted(common_birds):
                print(f"  - {bird}")
        else:
            print("\nNo birds found in all three forests")
            # Create empty CSV
            df = pd.DataFrame(columns=['scientific_name'])
            output_file = output_dir / "common_to_all_forests.csv"
            df.to_csv(output_file, index=False)
    else:
        print(f"\nNeed data from all 3 forests for this comparison")
        print(f"Currently have data from: {valid_forests}")
        # Create empty CSV
        df = pd.DataFrame(columns=['scientific_name'])
        output_file = output_dir / "common_to_all_forests.csv"
        df.to_csv(output_file, index=False)
    
    # 4. Summary statistics CSV
    print("\n\n4. SUMMARY STATISTICS:")
    print("-" * 40)
    
    summary_data = []
    for forest in ['one', 'two', 'three']:
        if forest in forest_birds:
            summary_data.append({
                'forest_type': forest,
                'total_unique_birds': len(forest_birds[forest]),
                'exclusive_birds': len(forest_birds[forest] - set().union(
                    *[forest_birds[f] for f in valid_forests if f != forest]
                )) if forest in valid_forests else 0
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        output_file = output_dir / "summary_statistics.csv"
        summary_df.to_csv(output_file, index=False)
        print(f"\nSummary statistics saved to: {output_file}")
        
        # Display summary
        print("\nForest Type | Total Birds | Exclusive Birds")
        print("-" * 40)
        for row in summary_data:
            print(f"{row['forest_type'].upper():11} | {row['total_unique_birds']:11} | {row['exclusive_birds']:15}")
    
    return valid_forests

def main():
    print("=" * 60)
    print("FOREST BIRD DISTRIBUTION ANALYSIS")
    print("=" * 60)
    print("Input: Excel files (.xlsx) with 'Beobachtungen' sheet")
    print("Output: CSV files in 'results' folder")
    print("Confidence threshold: > 0.8")
    print("Forest types: one, two, three")
    print("=" * 60)
    
    try:
        # Check if data folder exists
        if not Path("data").exists():
            print("ERROR: 'data' folder not found in current directory!")
            print("Please create a 'data' folder with subfolders: one, two, three")
            return
        
        # Process the data
        forest_data = process_forest_data()
        
        # Analyze and save results
        valid_forests = analyze_and_save_results(forest_data)
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"\nResults saved to 'results' folder:")
        print("  - [forest]_unique_birds.csv: All birds in each forest")
        print("  - [forest]_exclusive_birds.csv: Birds only in that forest")
        print("  - common_to_all_forests.csv: Birds in all three forests")
        print("  - summary_statistics.csv: Counts and statistics")
        print(f"\nProcessed data from {len(valid_forests)} forest(s): {valid_forests}")
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()