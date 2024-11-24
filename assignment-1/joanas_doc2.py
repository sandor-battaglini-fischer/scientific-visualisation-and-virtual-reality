import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import mplcursors

# Load the data
file_path = 'assignment-1/cars.csv'
data = pd.read_csv(file_path)

# Convert the 'year' column to a full year
data['full_year'] = data['year'].apply(lambda x: x + 1900 if x < 100 else x)

# Define a color map based on origin
origin_color_map = {'US': 'blue', 'Europe': 'green', 'Japan': 'red'}
data['color'] = data['origin'].map(origin_color_map)

# Define the symbol map for cylinders
cylinder_symbol_map = {
    3: 'o',      # circle
    4: 's',      # square
    5: 'D',      # diamond
    6: 'P',      # plus (filled)
    8: 'X'       # x (filled)
}

# Filter data to include only specified cylinder numbers
data = data[data['cylinders'].isin(cylinder_symbol_map.keys())]

# Add the cylinder_symbol column to the dataframe
data['cylinder_symbol'] = data['cylinders'].map(cylinder_symbol_map)

# Define offsets for origin as well as larger interval between years
origin_offset = {'US': -0.2, 'Europe': 0, 'Japan': 0.2}  # Smaller offsets between countries
year_interval_offset = 0.5  # Reduced offset between years (was 2.0)

# Create a new column with both the year offset and origin-based shift
data['full_year_offset'] = data.apply(
    lambda row: row['full_year'] + origin_offset[row['origin']],
    axis=1
)

# Calculate weight normalization like in visualisation.py
weight_norm = (data['weigth'] - data['weigth'].min()) / (data['weigth'].max() - data['weigth'].min())

# Calculate horsepower normalization like in visualisation.py
hp_norm = (data['horsepower'] - data['horsepower'].min()) / (data['horsepower'].max() - data['horsepower'].min())

# Define refined scaling function for marker sizes with more extreme scaling
def scale_marker_size(horsepower):
    min_size = 3
    max_size = 20
    normalized_hp = (horsepower - data['horsepower'].min()) / (data['horsepower'].max() - data['horsepower'].min())
    return min_size + (normalized_hp ** 1.5) * (max_size - min_size)

# Add scaled sizes to the dataframe
data['marker_size'] = data['horsepower'].apply(scale_marker_size)

# Create figure and axis with larger size for better readability
fig, ax = plt.subplots(figsize=(15, 10))

# Define unique years before using them
unique_years = sorted(data['full_year'].unique())

# Create minor ticks
minor_ticks = []
for year in unique_years:
    for offset in origin_offset.values():
        minor_ticks.append(year + offset)
        
# Correct the column name from 'weigth' to 'weight'
min_weight = data['weigth'].min()
max_weight = data['weigth'].max()

# Create scatter plot for each origin and cylinder combination
for origin in ['US', 'Europe', 'Japan']:
    for cylinders in cylinder_symbol_map.keys():
        mask = (data['origin'] == origin) & (data['cylinders'] == cylinders)
        subset = data[mask]
        if len(subset) > 0:  # Only plot if we have data for this combination
            scatter = ax.scatter(
                subset['full_year_offset'],
                subset['MPG'],
                s=subset['marker_size']*20,
                c=subset['weigth'],  # Corrected column name
                marker=cylinder_symbol_map[cylinders],
                cmap='viridis_r',
                alpha=0.7,
                vmin=min_weight,  # Set the minimum value for the color scale
                vmax=max_weight   # Set the maximum value for the color scale
            )

# Customize plot appearance
ax.set_title('Evolution of Car Characteristics in Europe, US, and Japan (1970-1982)', pad=20, fontsize=24)
ax.set_xlabel('Year/Origin', fontsize=20, labelpad=100)
ax.set_ylabel('Miles per Gallon (MPG)', fontsize=20)
ax.tick_params(axis='y', labelsize=15)

# Add gridlines
ax.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)  # Place gridlines behind the points

# Add minor gridlines for the three country positions per year
ax.set_xticks(minor_ticks, minor=True)
ax.grid(True, which='minor', linestyle=':', alpha=0.4)

# Adjust figure size and margins
fig.set_size_inches(18, 10)  # Maintain a balanced aspect ratio
plt.subplots_adjust(left=0.1, right=0.7, bottom=0.2, top=0.9)  # Adjusted margins

# Move x-axis label lower and adjust spacing
ax.set_xlabel('Year/Origin', fontsize=20, labelpad=100)

# Adjust the subplot parameters to make room for the labels
plt.subplots_adjust(bottom=0.2, right=0.85)

# Create custom x-axis ticks with origins and years
for year in unique_years:
    for origin, offset in origin_offset.items():
        if origin == 'Europe':
            # Add rotated origin text and horizontal year much lower
            ax.text(year + offset, ax.get_ylim()[0] , origin, 
                   rotation=90, ha='center', va='top', fontsize=15)
            ax.text(year + offset, ax.get_ylim()[0] - 5, str(year),  # Increased spacing here
                   rotation=0, ha='center', va='top', fontsize=15)
        else:
            # Just add rotated origin text
            ax.text(year + offset, ax.get_ylim()[0] -0.5, origin, 
                   rotation=90, ha='center', va='top', fontsize=15)

# Remove default ticks and labels
ax.set_xticks([])
ax.set_xticklabels([])

# Create comprehensive legend
legend_elements = []

# 1. Cylinder symbols
legend_elements.append(Line2D([0], [0], marker='none', linestyle='none', label='Number of Cylinders:'))
for cylinders, marker in cylinder_symbol_map.items():
    legend_elements.append(
        Line2D([0], [0], marker=marker, color='black', linestyle='none',
               markersize=10, label=f'{cylinders} cylinders')
    )

# 2. Horsepower (size) legend
legend_elements.append(Line2D([0], [0], marker='none', linestyle='none', label='\nHorsepower:'))
min_hp = int(data['horsepower'].min())
max_hp = int(data['horsepower'].max())
for hp, size in [(min_hp, 3), (max_hp, 20)]:
    legend_elements.append(
        Line2D([0], [0], marker='o', color='gray', linestyle='none',
               markersize=np.sqrt(size*20)/2,  # Adjust size to match scatter plot
               label=f'{hp} HP')
    )

# Add legend with adjusted position
ax.legend(handles=legend_elements,
         title='Visual Encodings',
         title_fontsize=18,
         fontsize=14,
         bbox_to_anchor=(1.0, 1),  # Positioned closer to the plot
         loc='upper left',
         frameon=True,
         edgecolor='black')

# Add colorbar for weight with adjusted height and position
cax = plt.axes([0.86, 0.2, 0.02, 0.4])  # Positioned next to the legend
cbar = plt.colorbar(scatter, cax=cax)
cbar.set_label('Weight (lbs)', fontsize=16, labelpad=15)
cbar.ax.tick_params(labelsize=12)

# Keep track of data for each scatter plot
scatter_points = []
scatter_data = []

for origin in ['US', 'Europe', 'Japan']:
    for cylinders in cylinder_symbol_map.keys():
        mask = (data['origin'] == origin) & (data['cylinders'] == cylinders)
        subset = data[mask]
        if len(subset) > 0:
            scatter = ax.scatter(
                subset['full_year_offset'],
                subset['MPG'],
                s=subset['marker_size']*20,
                c=subset['weigth'],
                marker=cylinder_symbol_map[cylinders],
                cmap='viridis_r',
                alpha=0.7,
                vmin=min_weight,  # Set the minimum value for the color scale
                vmax=max_weight   # Set the maximum value for the color scale
            )
            scatter_points.append(scatter)
            scatter_data.append(subset)

cursor = mplcursors.cursor(scatter_points, hover=True)

@cursor.connect("add")
def on_add(sel):
    # Find which scatter plot was selected
    scatter_index = scatter_points.index(sel.artist)
    # Get the corresponding subset of data
    subset = scatter_data[scatter_index]
    
    # Get the x and y coordinates of the selected point
    x, y = sel.target
    
    # Find the matching row in the subset
    mask = (subset['full_year_offset'] == x) & (subset['MPG'] == y)
    point_data = subset[mask].iloc[0]
    
    text = (f"Model: {point_data['model']}\n"
           f"MPG: {point_data['MPG']:.1f}\n"
           f"Weight: {point_data['weigth']} lbs\n"
           f"Horsepower: {point_data['horsepower']} HP\n"
           f"Cylinders: {point_data['cylinders']}\n"
           f"Origin: {point_data['origin']}")
    sel.annotation.set_text(text)

# Display the plot
plt.show()