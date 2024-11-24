import numpy as np
import matplotlib.pyplot as plt
from pyevtk.hl import gridToVTK

# Define parameters
nx, ny = 20, 20  # Grid resolution (number of grid points in x and y directions)
dx, dy = 1.0, 1.0  # Spatial step size (in inches, arbitrary units)
tolerance = 0.5  # Convergence tolerance in degrees Fahrenheit
max_iterations = 10000  # Maximum number of iterations for solver

# Initialize temperature grid with a constant temperature (90°F)
T = np.full((nx, ny), 90.0)

# Apply boundary conditions:
T[:, 0] = 32.0  # Left boundary (32°F)
T[:, -1] = 100.0  # Right boundary (100°F)
for j in range(ny):
    T[0, j] = 32.0 + j * (100.0 - 32.0) / (ny - 1)  # Bottom boundary (linear increase)
    T[-1, j] = 32.0 + j * (100.0 - 32.0) / (ny - 1)  # Top boundary (linear increase)

# Apply initial condition in the center (3x3 square)
center_start_x = nx // 2 - 1
center_end_x = nx // 2 + 2
center_start_y = ny // 2 - 1
center_end_y = ny // 2 + 2
T[center_start_x:center_end_x, center_start_y:center_end_y] = 2.0  # Set center to 2°F

# Iterative solver (Gauss-Seidel method with convergence check)
def solve_temperature(T):
    for iteration in range(max_iterations):
        max_change = 0  # Track maximum temperature change per iteration
        T_old = T.copy()
        
        # Loop through interior grid points (excluding boundaries and center)
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                if not (center_start_x <= i < center_end_x and center_start_y <= j < center_end_y):  # Skip center region
                    new_T = 0.25 * (T[i + 1, j] + T[i - 1, j] + T[i, j + 1] + T[i, j - 1])  # Update temperature
                    change = abs(new_T - T[i, j])
                    max_change = max(max_change, change)
                    T[i, j] = new_T  # Update temperature value at (i, j)
            
        # Check for convergence (max temperature change is below tolerance)
        if max_change < tolerance:
            print(f"Converged after {iteration + 1} iterations with max change {max_change:.4f}")
            break
    else:
        print("Reached maximum iterations without full convergence")

# Run the solver to update the temperature grid
solve_temperature(T)

# Visualization of the temperature distribution using Matplotlib
plt.figure(figsize=(8, 6))
plt.imshow(T, cmap='hot', interpolation='nearest')
plt.colorbar(label="Temperature (°F)")
plt.title("Temperature Distribution in 20x20 Grid")
plt.xlabel("X-axis (grid cells)")
plt.ylabel("Y-axis (grid cells)")
plt.show()

# Prepare data for VTK export (structured grid format)
T_3D = T.reshape((nx, ny, 1))  # Reshape to a 3D array (nx, ny, 1)

# Export to VTK format for ParaView visualization
# Define grid coordinates in x, y, and z
x_coords = np.arange(nx) * dx  # x coordinates (spacing in x direction)
y_coords = np.arange(ny) * dy  # y coordinates (spacing in y direction)
z_coords = np.array([0])  # Single slice in z direction (z = 0 for 2D simulation)

# Write the data to a VTK file (.vtr format)
gridToVTK("temperature_output_20x20", x_coords, y_coords, z_coords, 
          pointData={"Temperature": T_3D})  # "Temperature" as point data array

# Inform the user that the simulation is complete and the VTK file has been saved
print("Simulation and export complete. Load 'temperature_output_20x20.vtr' in ParaView to visualize.")
