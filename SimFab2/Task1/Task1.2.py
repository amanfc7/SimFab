
# To perform the operation of melting the sphere created in previous task

import viennals3d as vls

# for making a function for custom velocity field with velocity as -1:

class velocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        return -1.0  

# grid spacing: 

gridDelta = 0.5

# for creating the domain:

sphere = vls.Domain(gridDelta)

# now, to generate a sphere:

vls.MakeGeometry(sphere, vls.Sphere([0.0, 0.0, 0.0], 10.0)).apply()     # taking 10 units as radius of the sphere

# for initializing advection kernel and the velocity field:

advectionKernel = vls.Advect()
velocities = velocityField()

# to set the velocity field: 

advectionKernel.setVelocityField(velocities)
advectionKernel.insertNextLevelSet(sphere)

# to perform multiple advection steps for enhancing the melting effect:

advectionKernel.setAdvectionTime(6.0)         # taking time as 6 an 8 and melting velocity as -1
advectionKernel.apply()

# for extracting and saving the melted sphere's mesh:

mesh = vls.Mesh()
vls.ToSurfaceMesh(sphere, mesh).apply()
vls.VTKWriter(mesh, "sphere_melted.vtp").apply()

# to visualize the grid points:

grid_mesh = vls.Mesh()
vls.ToVoxelMesh(sphere, grid_mesh).apply()
vls.VTKWriter(grid_mesh, "sphere_grid.vtp").apply()

print("Sphere has been melted with velocity -1 and saved.")
