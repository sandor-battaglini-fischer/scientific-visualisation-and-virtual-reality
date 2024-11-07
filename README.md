# Car Characteristics Visualization (1970-1982)

## Overview
This project visualizes the evolution of car characteristics from 1970 to 1982, focusing on the relationships between MPG (Miles Per Gallon), horsepower, weight, engine configuration, and country of origin. The visualization uses multiple visual channels to encode different variables simultaneously.

## Data
The visualization uses the `cars.csv` dataset containing the following columns:
- model: Car model name
- MPG: Miles per gallon fuel efficiency
- cylinders: Number of engine cylinders (3-8)
- horsepower: Engine power (45-230 HP)
- weight: Vehicle weight (1600-5200 lbs)
- year: Manufacturing year (1970-1982)
- origin: Country/region of manufacture (US, Japan, Europe)

## Features
- **Interactive Visualization**: 
  - Hover over data points to see detailed car information
  - Hover over trendlines to see origin-specific statistics
  - Dynamic highlighting of origin groups

- **Visual Encodings**:
  - X-axis: Year
  - Y-axis: MPG
  - Marker shape: Number of cylinders (polygon sides match cylinder count)
  - Marker size: Horsepower (larger = more powerful)
  - Marker opacity: Weight (more opaque = heavier)
  - Marker color: Country of origin (US=blue, Japan=orange, Europe=green)
  - Dashed lines: MPG trends per origin

## Requirements
- Python 3.x
- Required packages:
  ```
  pandas
  matplotlib
  seaborn
  numpy
  mplcursors
  ```

## Installation
1. Clone the repository
2. Install required packages:
   ```bash
   pip install pandas matplotlib seaborn numpy mplcursors
   ```

## Usage
Run the visualization script:
```bash
python visualisation.py
```

The script will generate a high-resolution plot (`cars-highres.png`) and display the interactive visualization.

![Car Characteristics Visualization](assignment-1/cars-highres.png)


## Output
The visualization will be saved as `cars-highres.png` with a resolution of 500 DPI, suitable for publication or detailed viewing.

