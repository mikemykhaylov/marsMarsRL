import shapely

from mars_mars_env.entities.terrain import Terrain


def generate_polygon(terrain: Terrain):
    points = terrain.compute_points()
    terrain.polygon = shapely.geometry.LineString(points)
