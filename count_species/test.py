import pandas as pd

# Load data (works with both Excel and CSV)
df = pd.read_csv('data_new.csv')
print(f"Loaded {len(df)} total records from CSV")

# Filter for confidence > 0.8
df_filtered = df[df['confidence'] > 0.8]
print(f"Filtered to {len(df_filtered)} records with confidence > 0.8")

# Check if we have any data after filtering
if len(df_filtered) == 0:
    print("No records found with confidence > 0.8")
    print("Please check your confidence threshold or data")
else:
    # Count species occurrences
    species_counts = df_filtered['scientific_name'].value_counts().reset_index()
    species_counts.columns = ['scientific_name', 'count']

    # Add common names if available
    if 'common_name' in df_filtered.columns:
        common_names = df_filtered[['scientific_name', 'common_name']].drop_duplicates()
        species_counts = pd.merge(species_counts, common_names, on='scientific_name')

    # Sort by count (highest first)
    species_counts = species_counts.sort_values('count', ascending=False)

    # Save to CSV
    species_counts.to_csv('species_counts_high_confidence.csv', index=False)
    print(f"Saved {len(species_counts)} species counts to 'species_counts_high_confidence.csv'")

    # Print summary
    print(f"\nTotal records with confidence > 0.8: {len(df_filtered)}")
    print(f"Unique species with confidence > 0.8: {len(species_counts)}")
    
    # Calculate percentage of high-confidence detections
    percent_high_conf = (len(df_filtered) / len(df)) * 100
    print(f"Percentage of high-confidence detections: {percent_high_conf:.1f}%")
    
    print(f"\nTop 5 species (confidence > 0.8):")
    print(species_counts.head().to_string(index=False))