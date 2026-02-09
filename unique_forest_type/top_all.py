import pandas as pd

# Load the CSV data
df = pd.read_csv('gamba_bird_occurrences.csv')

# 1. All birds with at least one occurrence in each forest type
for forest in ['one', 'two', 'three']:
    # Filter birds with at least one occurrence in this forest
    forest_birds = df[df[forest] > 0].copy()
    
    # Sort by total occurrences (or by the specific forest count if preferred)
    forest_birds = forest_birds.sort_values('total_n', ascending=False)
    
    # Save to CSV
    forest_birds[['scientific_name', 'common_name', forest, 'total_n']].to_csv(
        f'gamba_all_birds_in_forest_{forest}.csv', 
        index=False
    )
    print(f"Saved {len(forest_birds)} birds with at least one occurrence in forest {forest}")

# 2. All birds present in all three forest types (at least one in each)
# Filter birds with non-zero counts in all three forests
all_forests_birds = df[(df['one'] > 0) & (df['two'] > 0) & (df['three'] > 0)].copy()

# Sort by total occurrences
all_forests_birds = all_forests_birds.sort_values('total_n', ascending=False)

# Save to CSV
all_forests_birds[['scientific_name', 'common_name', 'one', 'two', 'three', 'total_n']].to_csv(
    'gamba_all_birds_in_all_forests.csv', 
    index=False
)
print(f"Saved {len(all_forests_birds)} birds present in all three forests")