import viennals3d as vls

# velocity field for deposition of Silicon:

class SiliconVelocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        top_surface_z = 2.0
        if abs(coord[2] - top_surface_z) < 0.1:  # condition to grow silicon on the top of oxide layer
            return 1.0  
        return 0.0  

    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0.0, 0.0, 1.0) 


# to create a Substrate:

# domain for the silicon substrate:

substrate_domain = vls.Domain()

min_corner_substrate = (-100, -100, -50)   
max_corner_substrate = (100, 100, 0)     

# to create the substrate as a box:

vls.MakeGeometry(substrate_domain, vls.Box(min_corner_substrate, max_corner_substrate)).apply()

# save the substrate:

substrate_mesh = vls.Mesh()
vls.ToSurfaceMesh(substrate_domain, substrate_mesh).apply()
vls.VTKWriter(substrate_mesh, "substrate.vtp").apply()

# to create a Oxide Layer plane:

print("Creating oxide layer...")

# domain for oxide layer:

oxide_domain = vls.Domain()

min_corner_oxide = (-100, -100, 0)      # 200x200 nm oxide plane, 2 nm height
max_corner_oxide = (100, 100, 2)     

# to create the oxide layer as a box:

vls.MakeGeometry(oxide_domain, vls.Box(min_corner_oxide, max_corner_oxide)).apply()

# save the oxide layer:

oxide_mesh = vls.Mesh()
vls.ToSurfaceMesh(oxide_domain, oxide_mesh).apply()
vls.VTKWriter(oxide_mesh, "oxide_layer.vtp").apply()
print("Oxide layer created and saved as 'oxide_layer.vtp'.")

# to create a domain for the silicon deposition:

print("Preparing silicon layer for deposition...")
silicon_domain = vls.Domain(oxide_domain)  

# to set up the velocity field for isotropic deposition:

velocities = SiliconVelocityField()

# to set up the advection kernel for deposition:

advection_kernel = vls.Advect()
advection_kernel.insertNextLevelSet(oxide_domain)  
advection_kernel.insertNextLevelSet(silicon_domain)  

# configure the advection kernel with the velocity field for deposition:

advection_kernel.setVelocityField(velocities)
advection_kernel.setIgnoreVoids(True) 

# to perform deposition using advection cycles:

print("Performing silicon deposition...")

deposition_steps = 50  # Number of deposition cycles
deposition_thickness = 50.0  # silicon thickness in nm
advection_time_per_step = deposition_thickness / deposition_steps

for step in range(deposition_steps):
    advection_kernel.setAdvectionTime(advection_time_per_step)  
    advection_kernel.apply()  

    # for saving each deposition step for visualization:

    silicon_mesh = vls.Mesh()
    vls.ToSurfaceMesh(silicon_domain, silicon_mesh).apply()
    vls.VTKWriter(silicon_mesh, f"silicon_deposition_step_{step + 1}.vtp").apply()
    

# to save the final silicon layer after deposition:

print("Final silicon layer saved after deposition.")
vls.ToSurfaceMesh(silicon_domain, silicon_mesh).apply()
vls.VTKWriter(silicon_mesh, "final_silicon_layer.vtp").apply()

# create the Mask (a 20nm wide box on top of deposited silicon):

print("Creating mask...")

mask_domain = vls.Domain()

min_corner_mask = (-10, -100, 52)  
max_corner_mask = (10, 100, 52)    

# create the mask as a box:

vls.MakeGeometry(mask_domain, vls.Box(min_corner_mask, max_corner_mask)).apply()

# save the mask for visualization:

mask_mesh = vls.Mesh()
vls.ToSurfaceMesh(mask_domain, mask_mesh).apply()
vls.VTKWriter(mask_mesh, "silicon_mask.vtp").apply()
print("Mask created and saved as 'silicon_mask.vtp'.")

# directional Etching of Silicon to create the fin:

class LeftEtchVelocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):    
        if normal[2] < 0 and coord[0] < min_corner_mask[0]:     # change "normal[2] < 0" to "normal[2] < 1" for slightly skewed
            return -1.0    # negative velocity for etch
        return 0.0 

    def getVectorVelocity(self, coord, material, normal, pointId):
        
        return (0.0, 0.0, 0.0)    # Change this to (0.1, 0.0, 0.2) for some isotropy to the directional process

# create an etching domain:
etch_domain = vls.Domain(mask_domain) 

# velocity field for directional etching:
etch_velocities = LeftEtchVelocityField()

# advection kernel for etching:

etch_kernel = vls.Advect()
etch_kernel.insertNextLevelSet(etch_domain)   
etch_kernel.insertNextLevelSet(silicon_domain)  

# Configure the advection kernel for directional etching:
etch_kernel.setVelocityField(etch_velocities)

# etch_kernel.setIntegrationScheme(vls.IntegrationSchemeEnum.LAX_FRIEDRICHS_1ST_ORDER)  
# (uncomment the above line to use Lax-Friedrichs scheme for the directional etch)  

etch_kernel.setIgnoreVoids(True) 

# Perform directional etching to create the fin:
print("Performing directional etch to create the fin...")

etch_steps = 6  
etch_depth = 60.0 
etch_time_per_step = etch_depth / etch_steps

for step in range(etch_steps):
    etch_kernel.setAdvectionTime(etch_time_per_step) 
    etch_kernel.apply()  

    # to save each etching step for visualization:

    fin_mesh = vls.Mesh()
    vls.ToSurfaceMesh(etch_domain, fin_mesh).apply()
    vls.VTKWriter(fin_mesh, f"left_side_etch_step_{step + 1}.vtp").apply()
    


vls.ToSurfaceMesh(etch_domain, fin_mesh).apply()
vls.VTKWriter(fin_mesh, "left_silicon_fin.vtp").apply()



# Right-Side Etching of Silicon:

class RightEtchVelocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):  
        if normal[2] < 0 and coord[0] > max_corner_mask[0]:        # change "normal[2] < 0" to "normal[2] < 1" for slightly skewed
            return -1.0  
        return 0.0  

    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0.0, 0.0, 0.0)      # Change this to (0.1, 0.0, 0.2) for some isotropy to the directional process

# etch domain for right side:
etch_domain_right = vls.Domain(silicon_domain)  

#  velocity field for right-side etching:
right_etch_velocities = RightEtchVelocityField()

# advection kernel for right-side etching:
right_etch_kernel = vls.Advect()
right_etch_kernel.insertNextLevelSet(etch_domain_right)  

right_etch_kernel.setVelocityField(right_etch_velocities)

# right_etch_kernel.setIntegrationScheme(vls.IntegrationSchemeEnum.LAX_FRIEDRICHS_1ST_ORDER)  
# (uncomment the above line to use Lax-Friedrichs scheme for the directional etch)  

right_etch_kernel.setIgnoreVoids(True)  


etch_steps = 6
etch_depth = 60.0  
etch_time_per_step = etch_depth / etch_steps

for step in range(etch_steps):
    right_etch_kernel.setAdvectionTime(etch_time_per_step) 
    right_etch_kernel.apply()  

    # Save each etching step for visualization:
    fin_mesh_right = vls.Mesh()
    vls.ToSurfaceMesh(etch_domain_right, fin_mesh_right).apply()
    vls.VTKWriter(fin_mesh_right, f"right_side_etch_step_{step + 1}.vtp").apply()
    
# Mask Removal:

mask_domain = None    

# Saving the final silicon structure after right-side etching:
vls.ToSurfaceMesh(etch_domain_right, fin_mesh_right).apply()
vls.VTKWriter(fin_mesh_right, "final_silicon_fin_etched.vtp").apply()

print("Fin etching complete.")

# Spacer Deposition:

class SpacerVelocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        if coord[2] >= 2.0: 
            return 1.0 
        return 0.0  

    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0.0, 0.0, 0.0)

print("Starting isotropic spacer deposition...")

# to create a domain for spacer:
spacer_domain = vls.Domain(etch_domain_right) 

# Define the velocity field for isotropic deposition:
spacer_velocities = SpacerVelocityField()

# Set up the deposition kernel:
spacer_kernel = vls.Advect()
spacer_kernel.insertNextLevelSet(spacer_domain)
 
spacer_kernel.setVelocityField(spacer_velocities)
spacer_kernel.setIgnoreVoids(True)  

# Perform isotropic deposition of 5 nm spacer:
spacer_steps = 5         # Number of deposition cycles
spacer_thickness = 5.0   # Target spacer thickness in nm
spacer_time_per_step = spacer_thickness / spacer_steps

for step in range(spacer_steps):
    spacer_kernel.setAdvectionTime(spacer_time_per_step)
    spacer_kernel.apply()

    # Save each deposition step for visualization:
    spacer_mesh = vls.Mesh()
    vls.ToSurfaceMesh(spacer_domain, spacer_mesh).apply()
    vls.VTKWriter(spacer_mesh, f"spacer_deposition_step_{step + 1}.vtp").apply()

# Save the final spacer structure:
print("Final spacer layer saved after deposition.")
vls.ToSurfaceMesh(spacer_domain, spacer_mesh).apply()
vls.VTKWriter(spacer_mesh, "spacer_layer.vtp").apply()



# Gate Deposition:

class GateVelocityField(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        if coord[2] < 0:
            return 0.0  
        return 1.0  

    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0.0, 0.0, 0.0)  

print("Starting isotropic gate deposition...")

gate_domain = vls.Domain(spacer_domain)  
gate_velocities = GateVelocityField()  

gate_kernel = vls.Advect()
gate_kernel.insertNextLevelSet(gate_domain)  
gate_kernel.setVelocityField(gate_velocities)
gate_kernel.setIgnoreVoids(True)

# performing isotropic deposition of 80 nm gate material everywhere:
gate_steps = 8 
gate_thickness = 80.0  
gate_time_per_step = gate_thickness / gate_steps

for step in range(gate_steps):
    gate_kernel.setAdvectionTime(gate_time_per_step)
    gate_kernel.apply()  

    # Save each deposition step for visualization:
    gate_mesh = vls.Mesh()
    vls.ToSurfaceMesh(gate_domain, gate_mesh).apply()
    vls.VTKWriter(gate_mesh, f"gate_deposition_step_{step + 1}.vtp").apply()

# to save the final gate structure:
print("Final gate layer saved after deposition.")
vls.ToSurfaceMesh(gate_domain, gate_mesh).apply()
vls.VTKWriter(gate_mesh, "final_gate_layer.vtp").apply()

print("Gate deposition complete.")


cmp_plane_z = 72.0  # CMP plane at 72 nm (70 nm above oxide, which starts at 2 nm)

cmp_box_min_corner = (-200, -200, cmp_plane_z)  
cmp_box_max_corner = (200, 200, cmp_plane_z + 100)   

# Create the CMP box geometry:
cmp_box = vls.Box(cmp_box_min_corner, cmp_box_max_corner)

# Create a domain for the CMP box
cmp_box_domain = vls.Domain()
vls.MakeGeometry(cmp_box_domain, cmp_box).apply()

# forBoolean operation between the gate domain and the CMP box domain:
cmp_domain = vls.Domain(gate_domain)  # Create the CMP domain from the gate domain

vls.BooleanOperation(cmp_domain, cmp_box_domain, vls.BooleanOperationEnum.RELATIVE_COMPLEMENT).apply()

# to save the resulting domain after CMP operation:
result_mesh = vls.Mesh()
vls.ToSurfaceMesh(cmp_domain, result_mesh).apply()
vls.VTKWriter(result_mesh, "cmp_result.vtp").apply()

print("CMP operation completed and gate flattened.")

# Gate Mask (10 nm wide mask perpendicular to fin on top of gate):

gate_mask_domain = vls.Domain(cmp_domain)
min_corner_gate_mask = (-100, -5, cmp_plane_z)  # Box on top of gate
max_corner_gate_mask = (100, 5, cmp_plane_z)
vls.MakeGeometry(gate_mask_domain, vls.Box(min_corner_gate_mask, max_corner_gate_mask)).apply()

gate_mask_mesh = vls.Mesh()
vls.ToSurfaceMesh(gate_mask_domain, gate_mask_mesh).apply()
vls.VTKWriter(gate_mask_mesh, "gate_mask.vtp").apply()
print("Gate mask created.")

# Spacer Etch:

print("Starting spacer etch...")

class SpacerEtchFieldLeft(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        if normal[2] < 0 and coord[1] < -5.0:            
            return -1.0
        return 0.0
    
    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0.0, 0.0, 0.0)     # Change this to (0.1, 0.0, 0.2) for some isotropy to the directional process

spacer_etch_domain_left = vls.Domain(spacer_domain)  
spacer_etch_velocities_left = SpacerEtchFieldLeft()

spacer_etch_kernel_left = vls.Advect()
spacer_etch_kernel_left.insertNextLevelSet(spacer_etch_domain_left)

spacer_etch_kernel_left.setVelocityField(spacer_etch_velocities_left)

# spacer_etch_kernel_left.setIntegrationScheme(vls.IntegrationSchemeEnum.LAX_FRIEDRICHS_1ST_ORDER)  
# (uncomment the above line to use Lax-Friedrichs scheme for the directional etch)  

spacer_etch_kernel_left.setIgnoreVoids(True)

spacer_etch_steps_left = 10
spacer_etch_depth_left = 100 
spacer_etch_time_per_step_left = spacer_etch_depth_left / spacer_etch_steps_left

for step in range(spacer_etch_steps_left):
    spacer_etch_kernel_left.setAdvectionTime(spacer_etch_time_per_step_left)
    spacer_etch_kernel_left.apply()

    # Save each etching step for visualization:
    spacer_etch_mesh_left = vls.Mesh()
    vls.ToSurfaceMesh(spacer_etch_domain_left, spacer_etch_mesh_left).apply()
    vls.VTKWriter(spacer_etch_mesh_left, f"spacer_etch_step_left_{step + 1}.vtp").apply()

# Save the final left-side etched structure:
vls.ToSurfaceMesh(spacer_etch_domain_left, spacer_etch_mesh_left).apply()
vls.VTKWriter(spacer_etch_mesh_left, "final_left_spacer_etched.vtp").apply()

class SpacerEtchFieldRight(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        if normal[2] < 0 and coord[1] > 5.0:  
            return -1.0
        return 0.0
    
    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0.0, 0.0, 0.0)    # Change this to (0.1, 0.0, 0.2) for some isotropy to the directional process

spacer_etch_domain_right = vls.Domain(spacer_etch_domain_left)  
spacer_etch_velocities_right = SpacerEtchFieldRight()

spacer_etch_kernel_right = vls.Advect()
spacer_etch_kernel_right.insertNextLevelSet(spacer_etch_domain_right)

spacer_etch_kernel_right.setVelocityField(spacer_etch_velocities_right)

# spacer_etch_kernel_right.setIntegrationScheme(vls.IntegrationSchemeEnum.LAX_FRIEDRICHS_1ST_ORDER)  
# (uncomment the above line to use Lax-Friedrichs scheme for the directional etch)  

spacer_etch_kernel_right.setIgnoreVoids(True)

spacer_etch_steps_right = 10
spacer_etch_depth_right = 100 
spacer_etch_time_per_step_right = spacer_etch_depth_right / spacer_etch_steps_right

for step in range(spacer_etch_steps_right):
    spacer_etch_kernel_right.setAdvectionTime(spacer_etch_time_per_step_right)
    spacer_etch_kernel_right.apply()

    # Save each etching step for visualization:
    spacer_etch_mesh_right = vls.Mesh()
    vls.ToSurfaceMesh(spacer_etch_domain_right, spacer_etch_mesh_right).apply()
    vls.VTKWriter(spacer_etch_mesh_right, f"spacer_etch_step_right_{step + 1}.vtp").apply()

# Save the final left-side etched structure:
vls.ToSurfaceMesh(spacer_etch_domain_right, spacer_etch_mesh_right).apply()
vls.VTKWriter(spacer_etch_mesh_right, "final_right_spacer_etched.vtp").apply()

# Gate Patterning Etch:

# Left-Side Gate Patterning Etch:

print("Starting gate patterning etch for the left side...")


class GateEtchVelocityFieldLeft(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        if normal[2] < 0 and coord[1] < -5.0:           # change "normal[2] < 0" to "normal[2] < 1" for slightly skewed
            return -1.0
        return 0.0
    
    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0.0, 0.0, 0.0)    # Change this to (0.1, 0.0, 0.2) for some isotropy to the directional process

gate_etch_domain_left = vls.Domain(cmp_domain)  
gate_etch_velocities_left = GateEtchVelocityFieldLeft()

gate_etch_kernel_left = vls.Advect()
gate_etch_kernel_left.insertNextLevelSet(gate_etch_domain_left)

gate_etch_kernel_left.setVelocityField(gate_etch_velocities_left)

# gate_etch_kernel_left.setIntegrationScheme(vls.IntegrationSchemeEnum.LAX_FRIEDRICHS_1ST_ORDER)  
# (uncomment the above line to use Lax-Friedrichs scheme for the directional etch)

gate_etch_kernel_left.setIgnoreVoids(True)

gate_etch_steps_left = 7
gate_etch_depth_left = 72.0  
gate_etch_time_per_step_left = gate_etch_depth_left / gate_etch_steps_left

for step in range(gate_etch_steps_left):
    gate_etch_kernel_left.setAdvectionTime(gate_etch_time_per_step_left)
    gate_etch_kernel_left.apply()

    # Save each etching step for visualization:
    gate_etch_mesh_left = vls.Mesh()
    vls.ToSurfaceMesh(gate_etch_domain_left, gate_etch_mesh_left).apply()
    vls.VTKWriter(gate_etch_mesh_left, f"gate_patterning_etch_step_left_{step + 1}.vtp").apply()

# Save the final left-side etched structure:
vls.ToSurfaceMesh(gate_etch_domain_left, gate_etch_mesh_left).apply()
vls.VTKWriter(gate_etch_mesh_left, "final_left_gate_patterned.vtp").apply()


# Right-Side Gate Patterning Etch:

print("Starting gate patterning etch for the right side...")

class GateEtchVelocityFieldRight(vls.VelocityField):
    def getScalarVelocity(self, coord, material, normal, pointId):
        if normal[2] < 0 and coord[1] > 5.0:          # change "normal[2] < 0" to "normal[2] < 1" for slightly skewed
            return -1.0
        return 0.0
    
    def getVectorVelocity(self, coord, material, normal, pointId):
        return (0.0, 0.0, 0.0)     # Change this to (0.1, 0.0, 0.2) for some isotropy to the directional process

gate_etch_domain_right = vls.Domain(gate_etch_domain_left) 
gate_etch_velocities_right = GateEtchVelocityFieldRight()

gate_etch_kernel_right = vls.Advect()
gate_etch_kernel_right.insertNextLevelSet(gate_etch_domain_right)

gate_etch_kernel_right.setVelocityField(gate_etch_velocities_right)

# gate_etch_kernel_right.setIntegrationScheme(vls.IntegrationSchemeEnum.LAX_FRIEDRICHS_1ST_ORDER)  
# (uncomment the above line to use Lax-Friedrichs scheme for the directional etch)

gate_etch_kernel_right.setIgnoreVoids(True)

gate_etch_steps_right = 7
gate_etch_depth_right = 72.0  
gate_etch_time_per_step_right = gate_etch_depth_right / gate_etch_steps_right

for step in range(gate_etch_steps_right):
    gate_etch_kernel_right.setAdvectionTime(gate_etch_time_per_step_right)
    gate_etch_kernel_right.apply()

    # Save each etching step for visualization:
    gate_etch_mesh_right = vls.Mesh()
    vls.ToSurfaceMesh(gate_etch_domain_right, gate_etch_mesh_right).apply()
    vls.VTKWriter(gate_etch_mesh_right, f"gate_patterning_etch_step_right_{step + 1}.vtp").apply()


# to remove the gate mask:
gate_mask_domain = None

# for saving the final etched gate:

vls.ToSurfaceMesh(gate_etch_domain_right, gate_etch_mesh_right).apply()
vls.VTKWriter(gate_etch_mesh_right, "final_right_gate_patterned.vtp").apply()

# Combine all domains into a single final domain:

final_domain = vls.Domain()

vls.BooleanOperation(final_domain, substrate_domain, vls.BooleanOperationEnum.UNION).apply()
vls.BooleanOperation(final_domain, oxide_domain, vls.BooleanOperationEnum.UNION).apply()
vls.BooleanOperation(final_domain, etch_domain_right, vls.BooleanOperationEnum.UNION).apply()
vls.BooleanOperation(final_domain, spacer_etch_domain_right, vls.BooleanOperationEnum.UNION).apply()
vls.BooleanOperation(final_domain, gate_etch_domain_right, vls.BooleanOperationEnum.UNION).apply()

# Save the final combined structure:

final_mesh = vls.Mesh()
vls.ToSurfaceMesh(final_domain, final_mesh).apply()
vls.VTKWriter(final_mesh, "FinFET_structure.vtp").apply()

print("FinFET process completed.")

