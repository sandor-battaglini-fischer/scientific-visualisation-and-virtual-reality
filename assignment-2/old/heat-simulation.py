from paraview.simple import *
from paraview import servermanager
import numpy as np
from vtkmodules import *
from vtkmodules.util import numpy_support
import vtk

class HeatDistributionSimulation:
    def __init__(self, grid_size=50):
        self.grid_size = grid_size
        self.temperature = np.zeros((grid_size, grid_size))
        self.initialize_conditions()
        self.iteration = 0
        
    def initialize_conditions(self):
        # Calculate physical positions
        inner_start = self.grid_size // 3
        inner_end = 2 * self.grid_size // 3
        
        # Initialize inner square (212°F)
        self.temperature[inner_start:inner_end, inner_start:inner_end] = 212
        
        # Initialize bottom edge (32°F)
        self.temperature[-1, :] = 32
        
        # Initialize top edge (100°F)
        self.temperature[0, :] = 100
        
        # Initialize sides with linear increase from 32°F to 100°F
        side_temps = np.linspace(32, 100, self.grid_size)
        self.temperature[:, 0] = side_temps[::-1]  # Left side
        self.temperature[:, -1] = side_temps[::-1]  # Right side

    def iterate(self):
        new_temp = np.copy(self.temperature)
        for i in range(1, self.grid_size-1):
            for j in range(1, self.grid_size-1):
                # Skip the fixed inner square
                inner_start = self.grid_size // 3
                inner_end = 2 * self.grid_size // 3
                if (inner_start <= i < inner_end and 
                    inner_start <= j < inner_end):
                    continue
                    
                # Apply the magic formula
                new_temp[i, j] = 0.25 * (
                    self.temperature[i-1, j] +  # Top
                    self.temperature[i+1, j] +  # Bottom
                    self.temperature[i, j-1] +  # Left
                    self.temperature[i, j+1]    # Right
                )
        
        max_change = np.max(np.abs(new_temp - self.temperature))
        self.temperature = new_temp
        self.iteration += 1
        return max_change

def create_visualization_pipeline():
    # Delete any existing pipelines, only if they exist
    try:
        Delete(GetActiveSource())
    except:
        pass
    
    # Create programmable source
    prog_source = servermanager.sources.ProgrammableSource()
    
    # Create simulation instance
    sim = HeatDistributionSimulation()
    
    # Convert the script functions to strings
    script_request_data_str = """
def RequestData():
    import vtk
    from vtkmodules.util import numpy_support
    import numpy as np
    
    # Create output
    mesh = vtk.vtkImageData()
    mesh.SetDimensions(sim.grid_size, sim.grid_size, 1)
    
    # Set spacing to match physical dimensions (9" x 9")
    spacing = 9.0 / (sim.grid_size - 1)
    mesh.SetSpacing(spacing, spacing, 1)
    
    # Create temperature array
    temp_array = numpy_support.numpy_to_vtk(sim.temperature.ravel(), deep=True)
    temp_array.SetName("Temperature")
    
    # Add temperature data to mesh points
    mesh.GetPointData().AddArray(temp_array)
    mesh.GetPointData().SetActiveScalars("Temperature")
    
    # Set output
    output = self.GetOutputDataObject(0)
    output.ShallowCopy(mesh)
    
    # Iterate simulation
    max_change = sim.iterate()
    if max_change < 0.01:  # Convergence criterion
        self.GetExecutive().SetContinueExecuting(0)
"""

    request_information_str = """
def RequestInformation():
    import vtk
    executive = self.GetExecutive()
    outInfo = executive.GetOutputInformation(0)
    
    # Set up time steps
    timesteps = list(range(1000))  # Max iterations
    outInfo.Set(executive.TIME_STEPS(), timesteps, len(timesteps))
    
    timeRange = [timesteps[0], timesteps[-1]]
    outInfo.Set(executive.TIME_RANGE(), timeRange, 2)
"""

    # Set the script strings
    prog_source.Script = script_request_data_str
    prog_source.ScriptRequestInformation = request_information_str
    prog_source.PythonPath = ''
    
    # Create visualization pipeline
    # Create the display
    display = Show(prog_source)
    
    # Set up color mapping
    lut = GetColorTransferFunction('Temperature')
    lut.RescaleTransferFunction(32.0, 212.0)
    lut.ApplyPreset('Cool to Warm', True)
    
    # Configure the color bar (updated properties)
    scalar_bar = GetScalarBar(lut, GetActiveView())
    scalar_bar.Title = 'Temperature (°F)'
    scalar_bar.ComponentTitle = ''
    scalar_bar.Position = [0.85, 0.25]
    scalar_bar.ScalarBarLength = 0.5  # Replaced Position2
    scalar_bar.Visibility = 1
    
    # Set up the view
    view = GetActiveView()
    if not view:
        view = CreateRenderView()
    
    # Configure view settings
    view.ViewSize = [800, 800]  # Set window size
    view.CameraPosition = [4.5, 4.5, 10.0]  # Center of the 9"x9" domain
    view.CameraFocalPoint = [4.5, 4.5, 0.0]
    view.CameraParallelScale = 5.0
    
    # Add annotations
    text = servermanager.sources.Text()
    text.Text = 'Heat Distribution Simulation'
    textDisplay = Show(text)
    textDisplay.WindowLocation = 'Upper Left Corner'
    
    # Update the display properties
    display.SetRepresentationType('Surface')
    display.LookupTable = lut
    display.ColorArrayName = ['POINTS', 'Temperature']
    
    # Add axes (corrected method)
    view = GetActiveView()
    view.AxesGrid.Visibility = 1
    view.AxesGrid.XTitle = 'Width (inches)'
    view.AxesGrid.YTitle = 'Height (inches)'
    view.AxesGrid.ZTitle = ''
    
    # Set the axes grid to use the data bounds
    view.AxesGrid.UseCustomBounds = 1
    view.AxesGrid.CustomBounds = [0, 9, 0, 9, 0, 0]
    
    # Set up animation
    animation = GetAnimationScene()
    animation.PlayMode = 'Snap To TimeSteps'
    animation.StartTime = 0
    animation.EndTime = 1000
    animation.NumberOfFrames = 1000
    
    # Update the view
    Render()
    
    return prog_source, display, view, animation

if __name__ == '__main__':
    # Create and start the visualization pipeline
    source, display, view, animation = create_visualization_pipeline()
    
    # Start the animation
    animation.Play()
    
    # Start the interactive loop
    Interact()