import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("="*60)
print("DIET ANALYSIS - TASK 1")
print("="*60)

# Load the dataset
print("\n[1/7] Loading dataset...")
df = pd.read_csv('All_Diets.csv')
print(f"✓ Dataset loaded successfully! Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Display first few rows
print("\n[2/7] First 5 rows of the dataset:")
print(df.head())

# Handle missing data
print("\n[3/7] Handling missing data...")
print("Missing values before cleaning:")
print(df.isnull().sum())

# Fill missing numeric values with mean
numeric_columns = ['Protein(g)', 'Carbs(g)', 'Fat(g)']
for col in numeric_columns:
    if col in df.columns:
        df[col].fillna(df[col].mean(), inplace=True)

print("\nMissing values after cleaning:")
print(df.isnull().sum())
print("✓ Data cleaned successfully!")

# Calculate average macronutrient content for each diet type
print("\n[4/7] Calculating average macronutrients per diet type...")
avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean()
print("\nAverage Macronutrients by Diet Type:")
print(avg_macros.round(2))
print("✓ Averages calculated!")

# Find top 5 protein-rich recipes for each diet type
print("\n[5/7] Finding top 5 protein-rich recipes per diet type...")
top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5)
print(f"\n✓ Found {len(top_protein)} top protein recipes across all diet types")
print("\nSample of top protein recipes:")
print(top_protein[['Diet_type', 'Recipe_name', 'Protein(g)']].head(10))

# Find diet type with highest protein content
print("\n[6/7] Finding diet with highest average protein...")
highest_protein_diet = avg_macros['Protein(g)'].idxmax()
highest_protein_value = avg_macros['Protein(g)'].max()
print(f"\n✓ Diet type with highest protein: {highest_protein_diet}")
print(f"  Average protein content: {highest_protein_value:.2f}g")

# Identify most common cuisines for each diet type
print("\n[7/7] Finding most common cuisines per diet type...")
most_common_cuisines = df.groupby('Diet_type')['Cuisine_type'].agg(lambda x: x.mode()[0] if not x.mode().empty else 'N/A')
print("\nMost Common Cuisine by Diet Type:")
print(most_common_cuisines)

# Add new metrics
print("\nCreating new metrics (ratios)...")
df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / (df['Carbs(g)'] + 0.001)
df['Carbs_to_Fat_ratio'] = df['Carbs(g)'] / (df['Fat(g)'] + 0.001)

print("✓ New metrics added!")
print("\nSample of new metrics:")
print(df[['Recipe_name', 'Protein_to_Carbs_ratio', 'Carbs_to_Fat_ratio']].head())

# Save processed data
df.to_csv('All_Diets_processed.csv', index=False)
print("\n✓ Processed data saved to 'All_Diets_processed.csv'")

print("\n" + "="*60)
print("DATA ANALYSIS COMPLETE!")
print("="*60)

# VISUALIZATIONS
print("\n\nGenerating visualizations...\n")

# Visualization 1: Bar chart for average protein by diet type
print("[VIZ 1/5] Creating bar chart for average protein...")
plt.figure(figsize=(12, 6))
avg_macros['Protein(g)'].sort_values(ascending=False).plot(kind='bar', color='steelblue')
plt.title('Average Protein Content by Diet Type', fontsize=16, fontweight='bold')
plt.xlabel('Diet Type', fontsize=12)
plt.ylabel('Average Protein (g)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('viz1_avg_protein_by_diet.png', dpi=300, bbox_inches='tight')
print("✓ Saved as 'viz1_avg_protein_by_diet.png'")
plt.show()

# Visualization 2: Bar chart for all macronutrients
print("\n[VIZ 2/5] Creating grouped bar chart for all macronutrients...")
plt.figure(figsize=(14, 6))
avg_macros.plot(kind='bar', width=0.8)
plt.title('Average Macronutrient Content by Diet Type', fontsize=16, fontweight='bold')
plt.xlabel('Diet Type', fontsize=12)
plt.ylabel('Average Content (g)', fontsize=12)
plt.legend(title='Macronutrients', labels=['Protein', 'Carbs', 'Fat'])
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('viz2_all_macros_by_diet.png', dpi=300, bbox_inches='tight')
print("✓ Saved as 'viz2_all_macros_by_diet.png'")
plt.show()

# Visualization 3: Heatmap of macronutrients
print("\n[VIZ 3/5] Creating heatmap...")
plt.figure(figsize=(10, 8))
sns.heatmap(avg_macros, annot=True, fmt='.1f', cmap='YlOrRd', cbar_kws={'label': 'Grams'})
plt.title('Heatmap: Macronutrient Content by Diet Type', fontsize=16, fontweight='bold')
plt.xlabel('Macronutrients', fontsize=12)
plt.ylabel('Diet Type', fontsize=12)
plt.tight_layout()
plt.savefig('viz3_heatmap_macros.png', dpi=300, bbox_inches='tight')
print("✓ Saved as 'viz3_heatmap_macros.png'")
plt.show()

# Visualization 4: Scatter plot for top protein recipes
print("\n[VIZ 4/5] Creating scatter plot for top protein recipes...")
plt.figure(figsize=(14, 8))
for diet in top_protein['Diet_type'].unique():
    diet_data = top_protein[top_protein['Diet_type'] == diet]
    plt.scatter(diet_data['Cuisine_type'], diet_data['Protein(g)'], 
                label=diet, alpha=0.6, s=100)

plt.title('Top 5 Protein-Rich Recipes by Cuisine and Diet Type', fontsize=16, fontweight='bold')
plt.xlabel('Cuisine Type', fontsize=12)
plt.ylabel('Protein Content (g)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Diet Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('viz4_scatter_top_protein.png', dpi=300, bbox_inches='tight')
print("✓ Saved as 'viz4_scatter_top_protein.png'")
plt.show()

# Visualization 5: Distribution of protein across diets
print("\n[VIZ 5/5] Creating box plot for protein distribution...")
plt.figure(figsize=(14, 6))
sns.boxplot(data=df, x='Diet_type', y='Protein(g)', palette='Set2')
plt.title('Protein Distribution Across Diet Types', fontsize=16, fontweight='bold')
plt.xlabel('Diet Type', fontsize=12)
plt.ylabel('Protein (g)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('viz5_protein_distribution.png', dpi=300, bbox_inches='tight')
print("✓ Saved as 'viz5_protein_distribution.png'")
plt.show()

print("\n" + "="*60)
print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
print("="*60)
print("\nGenerated files:")
print("- viz1_avg_protein_by_diet.png")
print("- viz2_all_macros_by_diet.png")
print("- viz3_heatmap_macros.png")
print("- viz4_scatter_top_protein.png")
print("- viz5_protein_distribution.png")
print("- All_Diets_processed.csv")
print("\n✓ TASK 1 COMPLETE! Take screenshots now!")
print("="*60)