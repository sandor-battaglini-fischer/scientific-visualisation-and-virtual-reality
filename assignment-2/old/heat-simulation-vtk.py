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

def create_vtk_visualization(sim, num_steps=1000):
    def create_outline_actor(points_list, color=(0, 0, 0), thickness=3):
        """Helper function to create outline actors"""
        # Create points
        points = vtk.vtkPoints()
        for point in points_list:
            points.InsertNextPoint(point[0], point[1], point[2])
        
        # Create lines
        lines = vtk.vtkCellArray()
        for i in range(len(points_list)):
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, i)
            line.GetPointIds().SetId(1, (i + 1) % len(points_list))
            lines.InsertNextCell(line)
        
        # Create polydata
        polyData = vtk.vtkPolyData()
        polyData.SetPoints(points)
        polyData.SetLines(lines)
        
        # Create mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polyData)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(thickness)
        
        return actor

    def create_boundaries():
        # Create outer plate outline (9" × 9")
        plate_points = [
            (0, 0, -4),    # Bottom left
            (9, 0, -4),    # Bottom right
            (9, 0, 5),     # Top right
            (0, 0, 5),     # Top left
            (0, 0, -4),    # Back to start
        ]
        plate_actor = create_outline_actor(plate_points)
        
        heat_points = [
            (3, 0, -1),    # Bottom left
            (6, 0, -1),    # Bottom right
            (6, 0, 2),     # Top right
            (3, 0, 2),     # Top left
            (3, 0, -1),    # Back to start
        ]
        heat_actor = create_outline_actor(heat_points, color=(0, 0, 0))
        
        # Water surface line at z=0
        water_points = [
            (-0.5, 0, 0),     # Left
            (9.5, 0, 0),      # Right
        ]
        water_actor = create_outline_actor(water_points, color=(0, 0, 1))
        
        return [plate_actor, heat_actor, water_actor]

    def create_water_bath():
        # Create the water rectangle
        plane = vtk.vtkPlaneSource()
        plane.SetOrigin(-0.5, 0, -4.5)  # Slightly wider than plate
        plane.SetPoint1(9.5, 0, -4.5)
        plane.SetPoint2(-0.5, 0, 0)     # Up to water line
        
        water_mapper = vtk.vtkPolyDataMapper()
        water_mapper.SetInputConnection(plane.GetOutputPort())
        
        water_actor = vtk.vtkActor()
        water_actor.SetMapper(water_mapper)
        water_actor.GetProperty().SetColor(0.4, 0.7, 1.0)
        water_actor.GetProperty().SetOpacity(0.3)
        
        return [water_actor]

    def create_timestep_text():
        text_actor = vtk.vtkTextActor()
        text_actor.SetInput(f"Timestep: {sim.iteration}")
        text_actor.GetTextProperty().SetFontSize(24)
        text_actor.GetTextProperty().SetColor(0, 0, 0)
        text_actor.SetPosition(20, 20)
        return text_actor

    class AnimationCallback():
        def __init__(self, sim, text_actor, num_steps):
            self.sim = sim
            self.text_actor = text_actor
            self.num_steps = num_steps
            self.current_step = 0
            
        def execute(self, obj, event):
            # Perform multiple iterations per frame
            for _ in range(10):  # Do 10 iterations per frame
                max_change = self.sim.iterate()
                if max_change < 0.01 or self.current_step >= self.num_steps:
                    obj.DestroyTimer()
                    return
                self.current_step += 1
            
            self.update_visualization()
            self.text_actor.SetInput(f"Timestep: {self.sim.iteration}")
            render_window.Render()
            
        def update_visualization(self):
            points = vtk.vtkPoints()
            scalars = vtk.vtkFloatArray()
            scalars.SetName("Temperature")
            
            for i in range(sim.grid_size):
                x = 9.0 * i / (sim.grid_size - 1)
                for j in range(sim.grid_size):
                    z = 9.0 * j / (sim.grid_size - 1) - 4  # Scale to -4 to 5
                    points.InsertNextPoint(x, 0, z)
                    scalars.InsertNextValue(self.sim.temperature[i, j])
            
            grid.SetPoints(points)
            grid.GetPointData().SetScalars(scalars)
            mapper.Update()

    # Initial setup for temperature visualization
    points = vtk.vtkPoints()
    scalars = vtk.vtkFloatArray()
    scalars.SetName("Temperature")
    
    # Create initial points
    for i in range(sim.grid_size):
        x = 9.0 * i / (sim.grid_size - 1)
        for j in range(sim.grid_size):
            z = 4.0 * j / (sim.grid_size - 1) - 2
            points.InsertNextPoint(x, 0, z)
            scalars.InsertNextValue(sim.temperature[i, j])

    # Create the structured grid
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(sim.grid_size, 1, sim.grid_size)
    grid.SetPoints(points)
    grid.GetPointData().SetScalars(scalars)

    # Create color mapping with a clear color bar
    lut = vtk.vtkLookupTable()
    lut.SetHueRange(0.667, 0.0)  # Blue to red
    lut.SetTableRange(32, 212)    # Temperature range from 32°F to 212°F
    lut.SetNumberOfColors(256)
    lut.Build()

    # Create scalar bar (color bar)
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(lut)
    scalar_bar.SetTitle("Temperature (°F)")
    scalar_bar.SetNumberOfLabels(5)  # Show 5 labels
    scalar_bar.SetPosition(0.85, 0.2)  # Position in normalized viewport space
    scalar_bar.SetWidth(0.1)  
    scalar_bar.SetHeight(0.6)  
    scalar_bar.GetTitleTextProperty().SetColor(0, 0, 0) 
    scalar_bar.GetTitleTextProperty().SetFontSize(12)
    scalar_bar.GetLabelTextProperty().SetColor(0, 0, 0)
    scalar_bar.GetLabelTextProperty().SetFontSize(10)

    # Create mapper and actor for temperature visualization
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.SetLookupTable(lut)
    mapper.SetScalarRange(32, 212)

    plate_actor = vtk.vtkActor()
    plate_actor.SetMapper(mapper)

    # Create renderer and window
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    
    # Add fixed view interactor
    class Fixed2DInteractor(vtk.vtkInteractorStyleImage):
        def __init__(self):
            self.AddObserver("LeftButtonPressEvent", self.dummy_function)
            self.AddObserver("RightButtonPressEvent", self.dummy_function)
            self.AddObserver("MiddleButtonPressEvent", self.dummy_function)
            
        def dummy_function(self, obj, event):
            pass

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    interactor.SetInteractorStyle(Fixed2DInteractor())

    water_actors = create_water_bath()
    boundary_actors = create_boundaries()
    
    for actor in water_actors:
        renderer.AddActor(actor)
    renderer.AddActor(plate_actor)
    for actor in boundary_actors:
        renderer.AddActor(actor)
        
    renderer.SetBackground(1, 1, 1)

    # Add timestep text
    timestep_text = create_timestep_text()
    renderer.AddActor2D(timestep_text)

    # Add the scalar bar to the renderer
    renderer.AddActor2D(scalar_bar)

    # Adjust camera settings for correct proportions
    camera = renderer.GetActiveCamera()
    camera.SetPosition(4.5, -15, 0.5)
    camera.SetFocalPoint(4.5, 0, 0.5)
    camera.SetViewUp(0, 0, 1)
    camera.SetParallelProjection(True)
    camera.SetParallelScale(5)  # Adjusted to show full height

    # Set window size to maintain aspect ratio
    render_window.SetSize(900, 900)  # Square aspect ratio

    # Create and start animation with timestep text
    callback = AnimationCallback(sim, timestep_text, num_steps)
    interactor.Initialize()
    interactor.AddObserver('TimerEvent', callback.execute)
    interactor.CreateRepeatingTimer(10) 
    
    interactor.Start()

def save_to_vtk(sim, timestep, output_dir="vtk_output", filename_template="heat_simulation_{:03d}.vts"):
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
    # create_vtk_visualization(sim, num_timesteps)