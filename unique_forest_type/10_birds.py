import pandas as pd

# Load the CSV data
df = pd.read_csv('all_birds_forest_occurrences.csv')  # Replace with your actual filename

# 1. Top 10 birds for each forest type
for forest in ['one', 'two', 'three']:
    top_10 = df.nlargest(10, forest)[['scientific_name', 'common_name', forest, 'total_n']]
    top_10.to_csv(f'top_10_forest_{forest}.csv', index=False)

# 2. Top 10 birds present in all three forest types
# Filter birds with non-zero counts in all three forests
all_forests = df[(df['one'] > 0) & (df['two'] > 0) & (df['three'] > 0)]
top_10_all = all_forests.nlargest(10, 'total_n')[['scientific_name', 'common_name', 'one', 'two', 'three', 'total_n']]
top_10_all.to_csv('top_10_all_forests.csv', index=False)