
# Using multiple ,materials to create a snowman structure and then performing the melting using vsrious simulation methods

import viennals3d as vls

# for defining a custom velocity field with different velocities for each material:

class velocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        if material == 0:  # Bottom layer
            return -1.5  
        elif material == 1:  # Middle layer
            return -1.0 
        else:  # for top layer
            return -0.5 


gridDelta = 0.5

# creating domains for three spheres representing different materials:

sphere1 = vls.Domain(gridDelta)  # Bottom layer
sphere2 = vls.Domain(gridDelta)  # Middle layer
sphere3 = vls.Domain(gridDelta)  # Top layer

# the positions and sizes for the spheres:

vls.MakeGeometry(sphere1, vls.Sphere([0.0, 0.0, 0.0], 10.0)).apply()  # Bottom, radius = 10
vls.MakeGeometry(sphere2, vls.Sphere([0.0, 0.0, 12.0], 7.5)).apply()  # Middle, radius = 7.5
vls.MakeGeometry(sphere3, vls.Sphere([0.0, 0.0, 20.0], 5.0)).apply()  # Top, radius = 5

# for performing Boolean operations to wrap layers (starting from the top layer):

vls.BooleanOperation(sphere2, sphere3, vls.BooleanOperationEnum.UNION).apply()  # to combine middle and top
vls.BooleanOperation(sphere1, sphere2, vls.BooleanOperationEnum.UNION).apply()  # to combine bottom with the above

# to save the original snowman mesh (before melting):

combined_mesh = vls.Mesh()
vls.ToSurfaceMesh(sphere1, combined_mesh).apply()
vls.VTKWriter(combined_mesh, "snowman_combined_original.vtp").apply()

# for saving the individual layers:

vls.ToSurfaceMesh(sphere1, combined_mesh).apply()
vls.VTKWriter(combined_mesh, "snowman_bottom_original.vtp").apply()

vls.ToSurfaceMesh(sphere2, combined_mesh).apply()
vls.VTKWriter(combined_mesh, "snowman_middle_original.vtp").apply()

vls.ToSurfaceMesh(sphere3, combined_mesh).apply()
vls.VTKWriter(combined_mesh, "snowman_top_original.vtp").apply()

# to initialize advection kernel and velocity field:

advectionKernel = vls.Advect()
velocities = velocityField()

# now to set the velocity field and insert level sets:

advectionKernel.setVelocityField(velocities)
advectionKernel.insertNextLevelSet(sphere3)  
advectionKernel.insertNextLevelSet(sphere2)  
advectionKernel.insertNextLevelSet(sphere1)  

# performing advection for simulating the layer wrap:

advectionKernel.setAdvectionTime(2.0)     # this is the time for melting process
advectionKernel.apply()

# to extract and save the resulting mesh of snowman (after melting):

vls.ToSurfaceMesh(sphere1, combined_mesh).apply()
vls.VTKWriter(combined_mesh, "snowman_combined_melted.vtp").apply()

# saving also the individual parts after melting:

vls.ToSurfaceMesh(sphere1, combined_mesh).apply()
vls.VTKWriter(combined_mesh, "snowman_bottom_melted.vtp").apply()

vls.ToSurfaceMesh(sphere2, combined_mesh).apply()
vls.VTKWriter(combined_mesh, "snowman_middle_melted.vtp").apply()

vls.ToSurfaceMesh(sphere3, combined_mesh).apply()
vls.VTKWriter(combined_mesh, "snowman_top_melted.vtp").apply()

# to create visualization of grid points:

grid_mesh = vls.Mesh()
vls.ToVoxelMesh(sphere1, grid_mesh).apply()
vls.VTKWriter(grid_mesh, "snowman_melted_grid.vtp").apply()

print("Original and melted snowman have been saved.")
