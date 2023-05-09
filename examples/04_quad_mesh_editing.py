from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_quad.datastructures import PseudoQuadMesh

from compas_quad.grammar import delete_strip
from compas_quad.grammar import add_strip

import compas_rhino
from compas_rhino.artists import MeshArtist

from compas.utilities import pairwise


# ==============================================================================
# Input
# ==============================================================================

# Get input data.
mesh_guid = compas_rhino.select_mesh("Select a quad mesh to edit.")
pole_guids = compas_rhino.select_points("Select points as poles.")

# Wrap the inputs.
poles = [compas_rhino.rs.PointCoordinates(guid) for guid in pole_guids]
mesh = PseudoQuadMesh.from_vertices_and_faces_with_poles(compas_rhino.rs.MeshVertices(mesh_guid), compas_rhino.rs.MeshFaceVertices(mesh_guid), poles)
mesh.collect_strips()

# ==============================================================================
# Editing
# ==============================================================================

rule = compas_rhino.rs.GetString('Which grammar rule to apply?', strings=['add', 'delete'])

if rule == 'delete':

    # show strips
    compas_rhino.rs.EnableRedraw(False)
    dot2key = {}
    for skey in mesh.strips():
        edges = mesh.strip_edges(skey)
        pt = mesh.edge_midpoint(*edges[int(len(edges) / 2)])
        dot = compas_rhino.rs.AddTextDot(skey, pt)
        dot2key[dot] = skey
    compas_rhino.rs.EnableRedraw(True)

    # select strip
    dot = compas_rhino.rs.GetObject(message='Select strip for deletion.', filter=8192)
    skey = dot2key[dot]
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.DeleteObjects(dot2key.keys())
    compas_rhino.rs.EnableRedraw(True)

    # delete strip
    delete_strip(mesh, skey)
    print('Strip {} has been deleted.'.format(skey))
    
elif rule == 'add':
    
    # show vertices
    compas_rhino.rs.EnableRedraw(False)
    dot2key = {}
    for vkey in mesh.vertices():
        pt = mesh.vertex_coordinates(vkey)
        dot = compas_rhino.rs.AddTextDot(vkey, pt)
        dot2key[dot] = vkey
    compas_rhino.rs.EnableRedraw(True)
    
    # select vertices
    dots = compas_rhino.rs.GetObjects(message='Select polyedge for addition.', filter=8192)
    polyedge = [dot2key[dot] for dot in dots]
    compas_rhino.rs.EnableRedraw(False)
    compas_rhino.rs.DeleteObjects(dot2key.keys())
    compas_rhino.rs.EnableRedraw(True)
    is_valid = True
    for u, v in pairwise(polyedge):
        if not u in mesh.vertex_neighbors(v):
            is_valid = False
            print('Invalid polyedge - the vertices must represent a continutnous set of edges.')
    if polyedge[0] in mesh.vertex_neighbors(polyedge[-1]):
        if compas_rhino.rs.GetString('Close polyedge?', strings=['True', 'False']) == 'True':
            polyedge.append(polyedge[0])

    if is_valid:
        print(polyedge)
        add_strip(mesh, polyedge)
        mesh.smooth_centroid(kmax=1)
        print(polyedge)
        print('A strip has been added along polyedge {}.'.format(polyedge))

# ==============================================================================
# Visualization
# ==============================================================================

artist = MeshArtist(mesh, layer="Singular::CoarseMesh")
artist.clear_layer()
artist.draw_mesh()
