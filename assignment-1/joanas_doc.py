import pandas as pd
import plotly.express as px
import numpy as np

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
    3: 'circle',      
    4: 'square',      
    5: 'diamond',     
    6: 'cross',       
    8: 'x'            
}
data['cylinder_symbol'] = data['cylinders'].map(cylinder_symbol_map)

# Filter data to include only specified cylinder numbers
data = data[data['cylinders'].isin(cylinder_symbol_map.keys())]

# Define offsets for origin as well as larger interval between years
origin_offset = {'US': -0.4, 'Europe': 0, 'Japan': 0.4}  # Smaller origin offsets
year_interval_offset = 1.0  # Larger offset between years

# Create a new column with both the year offset and origin-based shift
data['full_year_offset'] = data['full_year'] + data['origin'].map(origin_offset) + (data['full_year'] * year_interval_offset)

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

# Create scatter plot with customized hover data and updated color palette
fig = px.scatter(
    data,
    x='full_year_offset',
    y='MPG',
    size='marker_size',
    size_max=20,
    color='weigth',
    symbol='cylinder_symbol',
    hover_name='model',
    hover_data={
        'color': False,
        'weigth': True,
        'horsepower': True,
        'cylinder_symbol': False
    },
    labels={
        'full_year_offset': 'Year',
        'MPG': 'Miles per Gallon',
        'weigth': 'Weight (lbs)',
        'horsepower': 'Horsepower'
    },
    title="Evolution of Car Characteristics (1970-1982)",
    color_continuous_scale="Viridis_r"
)

# Adjust axis titles, legend title, and color bar size and position
fig.update_layout(
    title=dict(
        text="Evolution of Car Characteristics (1970-1982)",
        font=dict(size=24),
        x=0.5,
        y=0.95
    ),
    xaxis_title=dict(text='Year/Origin', font=dict(size=20)),
    yaxis_title=dict(text='Miles per Gallon (MPG)', font=dict(size=20)),
    coloraxis_colorbar=dict(
        title=dict(
            text="Weight (lbs)",
            font=dict(size=16)
        ),
        thickness=15,
        len=0.6,
        x=1.02,
        y=0.5
    ),
    legend=dict(
        title=dict(
            text="Visual Encodings",
            font=dict(size=18)
        ),
        font=dict(size=14),
        x=1.15,
        y=0.99,
        xanchor='left',
        yanchor='top',
        bordercolor="black",
        borderwidth=1
    )
)

# Remove automatic legend entries
fig.for_each_trace(lambda t: t.update(showlegend=False))

# Add custom legend items with sections
# 1. Cylinder symbols
fig.add_scatter(x=[None], y=[None], mode='markers',
               marker=dict(size=0), name="<b>Number of Cylinders:</b>", showlegend=True)
for cylinders, shape in cylinder_symbol_map.items():
    fig.add_scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='black', symbol=shape),
        name=f'{cylinders} cylinders'
    )

# 2. Size legend (Horsepower)
min_hp = int(data['horsepower'].min())  # 46 HP
max_hp = int(data['horsepower'].max())  # 230 HP

fig.add_scatter(x=[None], y=[None], mode='markers',
               marker=dict(size=0), name="<b>Horsepower:</b>", showlegend=True)

# Create two manual legend entries with proper size difference
fig.add_scatter(
    x=[None], y=[None],
    mode='markers',
    marker=dict(
        size=3,  # Minimum size from scale_marker_size function
        color='gray',
        symbol='circle'
    ),
    name=f'{min_hp} HP',
    showlegend=True
)

fig.add_scatter(
    x=[None], y=[None],
    mode='markers',
    marker=dict(
        size=20,  # Maximum size from scale_marker_size function
        color='gray',
        symbol='circle'
    ),
    name=f'{max_hp} HP',
    showlegend=True
)

# # Ensure the legend items are not resized
# fig.update_layout(
#     legend=dict(
#         itemclick=False,        # Disable clicking to hide/show items
#         itemdoubleclick=False   # Disable double-clicking to isolate items
#     )
# )

# Set x-axis ticks to show distinct values for each origin-year combination
fig.update_xaxes(
    tickmode='array',
    tickvals=np.sort(data['full_year_offset'].unique()),
    ticktext=[
        f"{year}\n{origin}" for year in sorted(data['full_year'].unique()) 
        for origin in ['- US', '- Europe', '- Japan']
    ],
    tickangle=45,
    tickfont=dict(size=16)
)

# Update y-axis font size
fig.update_yaxes(tickfont=dict(size=14))

# Display the plot
fig.show()