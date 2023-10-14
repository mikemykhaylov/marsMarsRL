import shapely

from mars_mars_env.entities.terrain import Terrain


def update_terrain_polygon(terrain: Terrain, offset):
    terrain.polygon = shapely.transform(
        terrain.polygon, lambda point: point - [offset, 0]
    )
