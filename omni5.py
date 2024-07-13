import vtk
from vtkmodules.vtkRenderingCore import vtkRenderWindow, vtkRenderWindowInteractor
from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer
from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
import tkinter as tk
from tkinter import ttk
from threading import Thread
import time

# Parameters
outer_radius = 2
inner_radius = 1
height = 0.5
segments = 64
wear_rate = 0.01

# Create the tire geometry
def create_tire_geometry(outer_radius, inner_radius, height, segments):
    # Outer tire
    outer_cylinder = vtkCylinderSource()
    outer_cylinder.SetRadius(outer_radius)
    outer_cylinder.SetHeight(height)
    outer_cylinder.SetResolution(segments)

    # Inner tire
    inner_cylinder = vtkCylinderSource()
    inner_cylinder.SetRadius(inner_radius)
    inner_cylinder.SetHeight(height)
    inner_cylinder.SetResolution(segments)

    return outer_cylinder, inner_cylinder

# Create the tire actors
def create_tire_actor(cylinder, color):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cylinder.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    return actor

# Create the VTK rendering components
renderer = vtkOpenGLRenderer()
render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window_interactor = vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)
render_window_interactor.SetInteractorStyle(vtkInteractorStyleTrackballCamera())

# Create the tire geometry and actors
outer_cylinder, inner_cylinder = create_tire_geometry(outer_radius, inner_radius, height, segments)
colors = vtkNamedColors()
outer_actor = create_tire_actor(outer_cylinder, colors.GetColor3d('Gray'))
inner
