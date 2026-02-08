import pandas as pd

original = pd.read_csv('LaGamba2026ChirpityBirdNETspecies_list.csv')
new = pd.read_csv('forest_bird_occurrences.csv')

print(f"Original: {len(original)} rows")
print(f"New: {len(new)} rows")
print(f"Difference: {len(original) - len(new)} row")

# Find duplicates in original
duplicates = original[original.duplicated(subset=['scientific_name'], keep=False)]
if not duplicates.empty:
    print("\nDuplicates in original CSV:")
    print(duplicates[['scientific_name', 'common_name']])
else:
    print("\nNo duplicates in original CSV")

# Check for blank scientific names
blanks = original[original['scientific_name'].isna() | (original['scientific_name'].str.strip() == '')]
if not blanks.empty:
    print(f"\nBlank scientific names in original: {len(blanks)}")