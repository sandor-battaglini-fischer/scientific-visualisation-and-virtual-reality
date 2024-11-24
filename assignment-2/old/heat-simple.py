import vtk
import numpy as np

# Create a grid of data
grid_size = 50
temperature = np.zeros((grid_size, grid_size))
temperature.fill(50)  # Set all to 50°F for simplicity

# Convert numpy array to VTK array
vtk_data_array = vtk.vtkDoubleArray()
vtk_data_array.SetName("Temperature")
vtk_data_array.SetNumberOfComponents(1)
vtk_data_array.SetNumberOfTuples(grid_size * grid_size)
vtk_data_array.SetVoidArray(temperature.ravel(), grid_size * grid_size, 1)

# Create a VTK image data object
image_data = vtk.vtkImageData()
image_data.SetDimensions(grid_size, grid_size, 1)
image_data.GetPointData().SetScalars(vtk_data_array)

# Create a mapper and actor
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(image_data)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer, render window, and interactor
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Add the actor to the scene
renderer.AddActor(actor)
renderer.SetBackground(1, 1, 1)  # Background color white

# Render and interact
render_window.Render()
render_window_interactor.Start()