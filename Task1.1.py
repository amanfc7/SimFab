
# To create a Spherical surface using ViennaLS

import viennals3d as vls
import os

# to verify the current directory for working:

current_dir = os.getcwd()
print(f"Current working directory is: {current_dir}")

# for creating a simulation domain:

domain = vls.Domain()
print("Simulation domain has been created.")

# for creating a sphere centered at the origin with a given radius of 10 units:

radius = 10.0
center = [0.0, 0.0, 0.0]
sphere = vls.Sphere(center, radius)
vls.MakeGeometry(domain, sphere).apply()
print(f"Sphere of radius {radius} units has been created and applied on the domain.")

# now, to create a mesh object for the surface:

surface_mesh = vls.Mesh()
print("Surface mesh object has been created.")

# extracting the surface mesh:

ex_surface_mesh = vls.ToSurfaceMesh(domain, surface_mesh)
ex_surface_mesh.apply()
print("Surface mesh is extracted from the domain.")

# writing the surface mesh to a VTK file:

surface_file = "snowball_surface.vtk"
vtk_writer_surface = vls.VTKWriter(surface_mesh, surface_file)
vtk_writer_surface.apply()
print(f"Surface mesh file saved as: {surface_file}.")

# for creating a mesh object for the level set grid:

grid_mesh = vls.Mesh()
print("Grid mesh object has been created.")

# to extract the level set grid points and their values:

to_mesh = vls.ToMesh(domain, grid_mesh)
to_mesh.apply()
print("Level set grid points and values are extracted.")

# to write the grid mesh to a VTK file:

grid_file = "snowball_grid.vtk"
vtk_writer_grid = vls.VTKWriter(grid_mesh, grid_file)
vtk_writer_grid.apply()
print(f"Grid mesh is saved as: {grid_file}.")

# for confirmation of file creation:

files = [surface_file, grid_file]
for file in files:
    if os.path.isfile(os.path.join(current_dir, file)):
        print(f"File '{file}' has been successfully created and saved in current directory.")
    else:
        print(f"Error: File '{file}' cannot be found in the directory.")
