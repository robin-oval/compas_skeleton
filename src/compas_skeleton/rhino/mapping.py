from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs

from compas.datastructures import Network
from compas.datastructures import network_polylines
from compas.utilities import pairwise


__all__ = []

def surface_discrete_mapping(srf_guid, segment_length, minimum_discretisation=5, crv_guids=[], pt_guids=[]):
    """Map the boundaries of a Rhino NURBS surface to planar poylines dicretised within some discretisation
    using the surface UV parameterisation. Curve and point feautres on the surface can be included.

    Parameters
    ----------
    srf_guid : guid
        The guid of the surface.
    segment_length : float
        The target discretisation length of the surface boundaries.
    minimum_discretisation : int
        The minimum discretisation of the surface boundaries.
    crv_guids : list
        List of guids of curves on the surface.
    pt_guids : list
        List of guids of points on the surface.

    Returns
    -------
    tuple
        Tuple of the mapped objects: outer boundary, inner boundaries, polyline_features, point_features.
    """
    # a boundary may be made of multiple boundary components and therefore checking for closeness and joining are necessary
    borders = []
    for btype in (1, 2):
        border = []

        curves = rs.DuplicateSurfaceBorder(srf_guid, type=btype)
        exploded_curves = rs.ExplodeCurves(curves, delete_input=False)
        if len(exploded_curves) == 0:
            border_curves = curves
        else:
            rs.DeleteObjects(curves)
            border_curves = exploded_curves

        for guid in border_curves:
            L = rs.CurveLength(guid)
            N = max(int(L / segment_length) + 1, minimum_discretisation)
            points = []
            for point in rs.DivideCurve(guid, N):
                points.append(list(rs.SurfaceClosestPoint(srf_guid, point)) + [0.0])
            if rs.IsCurveClosed(guid):
                points.append(points[0])
            border.append(points)
            rs.DeleteObject(guid)
        borders.append(border)
    outer_boundaries = network_polylines(Network.from_lines([(u, v) for border in borders[0] for u, v in pairwise(border)]))
    inner_boundaries = network_polylines(Network.from_lines([(u, v) for border in borders[1] for u, v in pairwise(border)]))

    # mapping of the curve features on the surface
    curves = []
    for guid in crv_guids:
        L = rs.CurveLength(guid)
        N = max(int(L / segment_length) + 1, minimum_discretisation)
        points = []
        for point in rs.DivideCurve(guid, N):
            points.append(list(rs.SurfaceClosestPoint(srf_guid, point)) + [0.0])
        if rs.IsCurveClosed(guid):
            points.append(points[0])
        curves.append(points)
    polyline_features = network_polylines(Network.from_lines([(u, v) for curve in curves for u, v in pairwise(curve)]))

    # mapping of the point features onthe surface
    point_features = [list(rs.SurfaceClosestPoint(srf_guid, (rs.PointCoordinates(guid)))) + [0.0] for guid in pt_guids]

    return outer_boundaries[0], inner_boundaries, polyline_features, point_features


def surface_mesh_uv_to_xyz(surface, mesh):
    for vertex in mesh.vertices():
        xyz =  tuple(rs.EvaluateSurface(surface, *mesh.vertex_coordinates(vertex)[:2]))
        mesh.vertex_attributes(vertex, 'xyz', xyz)