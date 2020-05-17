"""
ArcGIS tools from Analysis Tools > Overlay
"""


def geom_contains(containerGeom, otherGeom):
    return containerGeom.contains(otherGeom)


def geom_intersect(geometry, intersectGeom, dimension):
    return geometry.intersect(intersectGeom, dimension)

