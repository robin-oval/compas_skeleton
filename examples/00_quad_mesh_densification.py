from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_quad.datastructures import CoarsePseudoQuadMesh

import compas_rhino
from compas_rhino.artists import MeshArtist

# ==============================================================================
# Input
# ==============================================================================

# Get input data.
mesh_guid = compas_rhino.select_mesh("Select a quad mesh to densify.")
pole_guids = compas_rhino.select_points("Select points as poles.")

# Wrap the inputs.
poles = [compas_rhino.rs.PointCoordinates(guid) for guid in pole_guids]

# Get the target length for the final quad mesh.
L = compas_rhino.rs.GetReal("Define the target edge length of the pattern.", 1.0)

# Densify the coarse mesh
coarsemesh = CoarsePseudoQuadMesh.from_vertices_and_faces_with_poles(compas_rhino.rs.MeshVertices(mesh_guid), compas_rhino.rs.MeshFaceVertices(mesh_guid), poles)
coarsemesh.collect_strips()
coarsemesh.set_strips_density_target(L)
coarsemesh.densification()#edges_to_curves=edge_curve)
densemesh = coarsemesh.dense_mesh()

# ==============================================================================
# Visualization
# ==============================================================================

artist = MeshArtist(densemesh, layer="Singular::DenseMesh")
artist.clear_layer()
artist.draw_mesh()
