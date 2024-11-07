import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
import matplotlib.path as mpath
import mplcursors


df = pd.read_csv('assignment-1/cars.csv')

origin_colors = {
    'US': '#1f77b4',
    'Japan': '#ff7f0e',
    'Europe': '#2ca02c'
}

def create_polygon_marker(n_sides):
    theta = np.linspace(0, 2*np.pi, n_sides+1)[:-1]
    x = np.cos(theta)
    y = np.sin(theta)
    vertices = np.column_stack((x, y))
    codes = [Path.MOVETO] + [Path.LINETO]*(n_sides-1) + [Path.CLOSEPOLY]
    vertices = np.vstack((vertices, vertices[0]))
    return Path(vertices, codes)

cylinder_markers = {
    3: create_polygon_marker(3),
    4: create_polygon_marker(4),
    5: create_polygon_marker(5),
    6: create_polygon_marker(6),
    8: create_polygon_marker(8)
}

plt.figure(figsize=(20, 12))

# Store trendlines and their corresponding scatter plots
trendlines = []
for origin in df['origin'].unique():
    mask = df['origin'] == origin
    X = df[mask]['year'].values.reshape(-1, 1)
    y = df[mask]['MPG'].values
    
    coefficients = np.polyfit(X.flatten(), y, 1)
    line = np.poly1d(coefficients)
    
    trendline = plt.plot(X, line(X), 
            color=origin_colors[origin], 
            linestyle='--', 
            alpha=0.5,
            linewidth=2,
            label=f'{origin} trend',
            picker=True)[0] 
    trendlines.append((trendline, origin))

hp_norm = (df['horsepower'] - df['horsepower'].min()) / (df['horsepower'].max() - df['horsepower'].min())
weight_norm = (df['weigth'] - df['weigth'].min()) / (df['weigth'].max() - df['weigth'].min())

legend_entries = set()
scatter_plots = []
for origin in df['origin'].unique():
    for cyl in sorted(df['cylinders'].unique()):
        mask = (df['origin'] == origin) & (df['cylinders'] == cyl)
        if mask.any():
            alphas = 0.15 + (0.85 * weight_norm[mask])
            sizes = 20 + (hp_norm[mask] * 800)
            scatter = plt.scatter(
                df[mask]['year'],
                df[mask]['MPG'],
                s=sizes,
                marker=cylinder_markers[cyl],
                c=[origin_colors[origin]],
                alpha=alphas,
                label=f'{origin} - {cyl} cyl'
            )
            scatter_plots.append((scatter, mask))
            legend_entries.add((origin, cyl))

plt.suptitle('Evolution of Car Characteristics (1970-1982)', 
            fontsize=24, 
            y=0.95,
            fontweight='bold')

plt.title('Comparison of common car characteristics for different origins and engine configurations', 
         pad=20, 
         fontsize=14,
         style='italic')

plt.xlabel('Year', fontsize=14, labelpad=10)
plt.ylabel('Miles per Gallon (MPG)', fontsize=14, labelpad=10)

years = sorted(df['year'].unique())
plt.xticks(years, [f'19{year}' for year in years], rotation=0, fontsize=12)
plt.yticks(fontsize=12)

legend_elements = []

legend_elements.append(plt.scatter([], [], c='none', alpha=0, s=0, label='\n$\mathbf{Country\ of\ Origin}$\n(incl. trendlines)'))
for origin, color in origin_colors.items():
    legend_elements.append(plt.scatter([], [], c=color, label=origin, marker='o', s=200))

legend_elements.append(plt.scatter([], [], c='none', alpha=0, s=0, label='\n$\mathbf{Engine\ Configuration}$'))
for cyl in sorted(cylinder_markers.keys()):
    if any((origin, cyl) in legend_entries for origin in origin_colors):
        legend_elements.append(plt.scatter([], [], c='gray', marker=cylinder_markers[cyl], 
                                         label=f'{cyl} cylinders', s=250))


hp_min = df['horsepower'].min()
hp_max = df['horsepower'].max()
weight_min = df['weigth'].min()
weight_max = df['weigth'].max()

legend_elements.append(plt.scatter([], [], c='none', alpha=0, s=0, label='\n$\mathbf{Horsepower}$'))
legend_elements.extend([
    plt.scatter([], [], c='gray', s=50, label=f'Low Horsepower (45hp)', alpha=0.7),
    plt.scatter([], [], c='gray', s=600, label=f'High Horsepower (230hp)', alpha=0.7)
])

legend_elements.append(plt.scatter([], [], c='none', alpha=0, s=0, label='\n$\mathbf{Weight}$'))
legend_elements.extend([
    plt.scatter([], [], c='gray', s=200, alpha=0.15, label=f'Low Weight (1600lbs)'),
    plt.scatter([], [], c='gray', s=200, alpha=1.0, label=f'High Weight (5200lbs)')
])

plt.legend(handles=legend_elements,
          fontsize=11,
          bbox_to_anchor=(1.02, 0.9),
          loc='upper left',
          borderaxespad=0,
          frameon=True,
          edgecolor='black',
          fancybox=True,
          shadow=True,
          labelspacing=1.5)


plt.subplots_adjust(right=0.85)

plt.grid(True, alpha=0.3)


scatter_objects = [scatter for scatter, mask in scatter_plots]
cursor = mplcursors.cursor(scatter_objects, hover=2)

@cursor.connect("add")
def on_add(sel):
    artist = sel.artist
    for scatter, mask in scatter_plots:
        if scatter == artist:
            df_filtered = df[mask]
            ind = sel.target
            if isinstance(ind, np.ma.MaskedArray):
                ind = np.where(~ind.mask)[0][0]
            row = df_filtered.iloc[ind]
            model_name = row['model'].title().replace(' Iii', ' III').replace(' Ii', ' II').replace(' Iv', ' IV')
            text = f"Model: {model_name}\nMPG: {row['MPG']:.1f}\nCylinders: {row['cylinders']}\nHorsepower: {row['horsepower']}\nWeight: {row['weigth']}\nYear: 19{row['year']}\nOrigin: {row['origin']}"
            sel.annotation.set_text(text)
            sel.annotation.get_bbox_patch().set(fc='white', alpha=0.8, ec='gray')
            sel.annotation.set_visible(True)
            break

@cursor.connect("remove")
def on_remove(sel):
    if sel and sel.annotation:
        sel.annotation.set_visible(False)
        plt.draw()


def on_move(event):
    if event.inaxes:
        hover_detected = False
        
        # Check for trendline hover
        for line, origin in trendlines:
            if line.contains(event)[0]:
                hover_detected = True
                # Get data for this origin
                origin_data = df[df['origin'] == origin]
                
                # Calculate yearly MPG changes
                yearly_data = origin_data.groupby('year')['MPG'].mean()
                total_years = yearly_data.index.max() - yearly_data.index.min()
                total_mpg_change = yearly_data.iloc[-1] - yearly_data.iloc[0]
                yearly_mpg_change_pct = (total_mpg_change / yearly_data.iloc[0]) * 100 / total_years
                
                # Calculate average MPG and horsepower
                avg_mpg = origin_data['MPG'].mean()
                avg_hp = origin_data['horsepower'].mean()
                
                # Calculate efficiency ratio (MPG per horsepower)
                efficiency_ratio = avg_mpg / avg_hp
                
                # Create and position annotation
                text = f"{origin}\nYearly MPG Change: {yearly_mpg_change_pct:.1f}%\nAvg MPG: {avg_mpg:.1f}\nMPG/HP Ratio: {efficiency_ratio:.3f}"
                if not hasattr(line, 'annotation'):
                    line.annotation = plt.annotate(text, xy=(0, 0), xytext=(10, 10),
                                                 textcoords='offset points',
                                                 bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8, ec='gray'),
                                                 visible=False)
                
                # Update annotation position
                line.annotation.xy = (event.xdata, event.ydata)
                line.annotation.set_visible(True)
                
                # Dim all scatter plots
                for scatter, mask in scatter_plots:
                    original_alphas = 0.15 + (0.85 * weight_norm[mask])
                    if df[mask]['origin'].iloc[0] == origin:
                        scatter.set_alpha(original_alphas)  # Keep original alpha for matching origin
                    else:
                        scatter.set_alpha(original_alphas * 0.1)  # Dim others
                break
        
        # If not hovering over a trendline, restore all alphas and hide annotations
        if not hover_detected:
            for scatter, mask in scatter_plots:
                original_alphas = 0.15 + (0.85 * weight_norm[mask])
                scatter.set_alpha(original_alphas)
            for line, _ in trendlines:
                if hasattr(line, 'annotation'):
                    line.annotation.set_visible(False)
        
        plt.draw()

# Connect the hover event
plt.gcf().canvas.mpl_connect('motion_notify_event', on_move)

plt.savefig('assignment-1/cars-highres.png', dpi=500)
plt.show()

