import numpy as np
import paraview.simple as pv
from vtkmodules.vtkCommonDataModel import vtkStructuredGrid
from vtkmodules.numpy_interface import dataset_adapter as dsa
from vtkmodules.vtkCommonCore import vtkPoints

class HeatDistributionSimulation:
    def __init__(self, grid_size=90):
        self.grid_size = grid_size
        self.temperature = np.zeros((grid_size, grid_size))
        self.initialize_conditions()
        self.iteration = 0
        
    def initialize_conditions(self):
        # Convert physical dimensions to grid points (9" x 4" plate)
        inner_start = self.grid_size // 3
        inner_end = 2 * self.grid_size // 3
        
        # Initialize the rye space to room temperature (70°F)
        self.temperature.fill(70)
        
        # Set the inner heat source (212°F)
        self.temperature[inner_start:inner_end, inner_start:inner_end] = 212
        
        # Set bottom edge (32°F)
        self.temperature[:, 0] = 32
        
        # Set top edge (100°F)
        self.temperature[:, -1] = 100
        
        # Set linear gradients on sides
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

def create_data():
    # This function will be called by ParaView
    sim = HeatDistributionSimulation()
    
    # Perform some iterations
    for _ in range(100):
        max_change = sim.iterate()
        if max_change < 0.01:
            break
    
    # Create VTK grid using vtk directly since we're in ParaView
    grid = vtkStructuredGrid()
    grid.SetDimensions(sim.grid_size, 1, sim.grid_size)
    
    # Create points
    points = vtkPoints()
    points.SetNumberOfPoints(sim.grid_size * sim.grid_size)
    
    # Create temperature array
    temperature_array = np.zeros(sim.grid_size * sim.grid_size)
    
    idx = 0
    for i in range(sim.grid_size):
        x = 9.0 * i / (sim.grid_size - 1)
        for j in range(sim.grid_size):
            z = 9.0 * j / (sim.grid_size - 1) - 4
            points.SetPoint(idx, x, 0, z)
            temperature_array[idx] = sim.temperature[i, j]
            idx += 1
    
    grid.SetPoints(points)
    
    # Convert temperature array to VTK array
    temp_vtk = dsa.numpyTovtkDataArray(temperature_array, "Temperature")
    grid.GetPointData().AddArray(temp_vtk)
    
    return grid

# For testing in Python
if __name__ == '__main__':
    # Create the programmable source
    prog_source = pv.ProgrammableSource()
    prog_source.OutputDataSetType = 'vtkStructuredGrid'
    
    # Define the RequestInformation Script
    prog_source.ScriptRequestInformation = ''
    
    # Define the main script
    def execute_script(algorithm):
        output = algorithm.GetOutput()
        output.ShallowCopy(create_data())
    
    # Assign the script
    prog_source.PythonScript = execute_script
    
    # Update the source
    prog_source.UpdatePipeline()
    
    # Create a better looking visualization
    display = pv.Show(prog_source)
    
    # Set up color mapping
    display.ColorArrayName = 'Temperature'
    display.LookupTable = pv.GetLookupTableForArray(
        'Temperature', 
        point_data=True,
        RGBPoints=[32.0, 0.0, 0.0, 1.0,
                  212.0, 1.0, 0.0, 0.0],
        ColorSpace='HSV'
    )
    
    # Set up the view
    view = pv.GetActiveView()
    if not view:
        view = pv.CreateRenderView()
    
    # Set camera position
    view.CameraPosition = [4.5, -15, 0.5]
    view.CameraFocalPoint = [4.5, 0, 0.5]
    view.CameraViewUp = [0.0, 0.0, 1.0]
    view.CameraParallelProjection = 1
    
    # Show color bar
    display.SetScalarBarVisibility(view, True)
    
    # Reset the view to fit data
    view.ResetCamera()