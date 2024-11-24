import vtk
import numpy as np
import os

class HeatDistributionSimulation:
    def __init__(self, grid_size=90):
        self.grid_size = grid_size
        self.temperature = np.zeros((grid_size, grid_size))
        self.initialize_conditions()
        self.iteration = 0
        
    def initialize_conditions(self):
        inner_start = self.grid_size // 3 
        inner_end = 2 * self.grid_size // 3  
        
        self.temperature.fill(70)
        
        self.temperature[inner_start:inner_end, inner_start:inner_end] = 212
        
        self.temperature[:, 0] = 32
        
        self.temperature[:, -1] = 100
        
        for i in range(self.grid_size):
            t = 32 + (100 - 32) * (i / (self.grid_size - 1))
            self.temperature[0, i] = t 
            self.temperature[-1, i] = t

    def iterate(self):
        new_temp = np.copy(self.temperature)
        inner_start = self.grid_size // 3
        inner_end = 2 * self.grid_size // 3
        
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                if (inner_start <= i < inner_end and 
                    inner_start <= j < inner_end):
                    continue
                    
                new_temp[i, j] = 0.25 * (
                    self.temperature[i-1, j] +
                    self.temperature[i+1, j] +
                    self.temperature[i, j-1] +
                    self.temperature[i, j+1]
                )
        
        max_change = np.max(np.abs(new_temp - self.temperature))
        self.temperature = new_temp
        self.iteration += 1
        return max_change

def save_to_vtk(sim, timestep, output_dir="vtk_outpu_2", filename_template="heat_simulation_{:03d}.vts"):
    """Save the current temperature grid to a VTK file."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = os.path.join(output_dir, filename_template.format(timestep))
    points = vtk.vtkPoints()
    scalars = vtk.vtkFloatArray()
    scalars.SetName("Temperature")
    
    for i in range(sim.grid_size):
        x = 9.0 * i / (sim.grid_size - 1)
        for j in range(sim.grid_size):
            y = 9.0 * j / (sim.grid_size - 1)
            points.InsertNextPoint(x, y, 0)
            scalars.InsertNextValue(sim.temperature[i, j])
    
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(sim.grid_size, sim.grid_size, 1)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalars)
    
    writer = vtk.vtkXMLStructuredGridWriter()
    writer.SetFileName(filename)
    writer.SetInputData(grid)
    writer.Write()

if __name__ == '__main__':
    sim = HeatDistributionSimulation()
    num_timesteps = 1500
    for timestep in range(num_timesteps):
        sim.iterate()
        save_to_vtk(sim, timestep)