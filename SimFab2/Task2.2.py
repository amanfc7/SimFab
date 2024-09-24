
# Creating a mask and substrate and using Bosch process to to simluate the process of making hole in the mask and substrate 

import viennals3d as vls

# Creating velocity field for deposition:

class velocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        return 1  # Uniform deposition rate

    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0, 0, 0)

# to define the grid extent and resolution:

extent = 40
gridDelta = 1
bounds = (-extent, extent, -extent, extent, -extent, extent)
boundarycons = (0, 0, 1)         # using Reflective boundaries in x and y, and Infinite in z

# to create the substrate (silicon) as a plane:

substrate = vls.Domain(bounds, boundarycons, gridDelta)
origin = (0, 0, 0)
planenormal = (0, 0, 1)
vls.MakeGeometry(substrate, vls.Plane(origin, planenormal)).apply()

# now to create the trench geometry on the substrate:

trench = vls.Domain(bounds, boundarycons, gridDelta)
minCorner = (-extent - 1, -extent / 4.0, -15.0)
maxCorner = (extent + 1, extent / 4.0, 15.0)
vls.MakeGeometry(trench, vls.Box(minCorner, maxCorner)).apply()
vls.BooleanOperation(substrate, trench, vls.BooleanOperationEnum.RELATIVE_COMPLEMENT).apply()

# to create the mask layer, on top of the substrate:

mask_layer = vls.Domain(bounds, boundarycons, gridDelta)
mask_thickness = 1  # thickness of the mask layer
mask_origin = (0, 0, mask_thickness)
vls.MakeGeometry(mask_layer, vls.Plane(mask_origin, planenormal)).apply()
vls.BooleanOperation(mask_layer, substrate, vls.BooleanOperationEnum.INTERSECT).apply()

# creating Advection setup for the deposition process:

velocities = velocityField()
advectionKernel = vls.Advect()
advectionKernel.insertNextLevelSet(substrate)  # Substrate layer
advectionKernel.insertNextLevelSet(mask_layer)  # Mask layer
advectionKernel.setVelocityField(velocities)

# to Advect and output the results:

counter = 1
passed_time = 0
mesh = vls.Mesh()
while passed_time < 4:
    advectionKernel.apply()
    passed_time += advectionKernel.getAdvectedTime()


 # to get output of the mask and substrate as separate meshes:

    vls.ToSurfaceMesh(mask_layer, mesh).apply()
    vls.VTKWriter(mesh, f"mask-{counter}.vtp").apply()

    vls.ToSurfaceMesh(substrate, mesh).apply()
    vls.VTKWriter(mesh, f"substrate-{counter}.vtp").apply()

    counter += 1

print(f"Time passed during the advection process = : {passed_time}")

# to create a circular hole in the mask layer:

hole_radius = 10
hole_height = 40
hole_cylinder = vls.Domain(bounds, boundarycons, gridDelta)
cylinder_center = (0, 0, 0)
cylinder_axis = (0, 0, 1)
vls.MakeGeometry(hole_cylinder, vls.Cylinder(cylinder_center, cylinder_axis, hole_radius, hole_height)).apply()

# to subtract the hole from the mask layer using Boolean operation:

vls.BooleanOperation(mask_layer, hole_cylinder, vls.BooleanOperationEnum.RELATIVE_COMPLEMENT).apply()

# Now, output the mask layer with the hole
mesh = vls.Mesh()
vls.ToSurfaceMesh(mask_layer, mesh).apply()  # Convert the mask layer (after hole creation) to a mesh
vls.VTKWriter(mesh, "mask_with_hole.vtp").apply()  # Save the mesh as a VTP file

# now, Set up for the Bosch process:

deposition_rate = 1
etch_rate = 1

# to define velocity fields for deposition and etching:

class depositionVelocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        return deposition_rate

class etchVelocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        return -etch_rate     # negative for etching

deposition_velocities = depositionVelocityField()
etch_velocities = etchVelocityField()

# for iteration of the Bosch process through several cycles:

num_cycles = 12
for cycle in range(num_cycles):
    print(f"Cycle {cycle + 1}")
    
    # Deposition step:

    advectionKernel.setVelocityField(deposition_velocities)
    advectionKernel.apply()
    
    # Etching step for hole in mask:
    
    advectionKernel.setVelocityField(etch_velocities)
    advectionKernel.apply()

    # etching step for hole in substrate:

    advectionKernel.setVelocityField(etch_velocities)
    advectionKernel.apply()

# Output results:

mesh = vls.Mesh()
vls.ToSurfaceMesh(substrate, mesh).apply()
vls.VTKWriter(mesh, f"substrate-cycle-{cycle+1}.vtp").apply()

vls.ToSurfaceMesh(mask_layer, mesh).apply()
vls.VTKWriter(mesh, f"mask-cycle-{cycle+1}.vtp").apply()
