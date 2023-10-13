import shapely

from entities.terrain import Terrain


def update_terrain_polygon(terrain: Terrain, offset):
    terrain.polygon = shapely.transform(
        terrain.polygon, lambda point: point - [offset, 0]
    )
