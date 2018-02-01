from shapely import geometry
from sqlalchemy import func, type_coerce
from geoalchemy2.shape import from_shape

from seahouse import db
from seahouse.ahn.models import AHNRaster, RasterIntersection


def generate_elevation_profile(line):
    """
    Follow the given line along our raster data (which contains the
    height), and return an elevation profile based on this data.

    This "line following" can be done using the following SQL Common Table
    Expression:

    .. code-block:: sql

        WITH line AS (
            SELECT ST_Transform(
                'SRID=4326;LINESTRING()'::geometry, 28992) AS geom
            )
        ),
        cells AS (
            SELECT
                ST_Centroid(
                    (ST_Intersection(ahn_raster.rast, line.geom)).geom
                ) AS geom,
                (ST_Intersection(ahn_raster.rast, line.geom)).val AS val
            FROM ahn_raster, line
            WHERE ST_Intersects(ahn_raster.rast, line.geom)
        ),
        height_data AS (
            SELECT ST_Transform(
                ST_SetSrid(
                    ST_MakePoint(
                        ST_X(cells.geom), ST_Y(cells.geom), cells.val
                    ),
                    28992
                ), 4326
            ) AS geom
            FROM cells, line
            ORDER BY ST_Distance(ST_StartPoint(line.geom), cells.geom)
        )
        SELECT height_data.geom FROM height_data;

    This SQL query is inspired by:
    http://blog.mathieu-leplatre.info/drape-lines-on-a-dem-with-postgis.html


    :param line: A shapely Linestring object
    :type line: geometry.LineString
    :return: An SQLAlchemy query object. The query returns rows with
             Point(x, y, height) objects.
    """

    elem = from_shape(line, 4326)
    line_cte = db.session.query(
            func.ST_Transform(elem, 28992).label("geom")).cte(name="line")

    cells_cte = db.session.query(
        # Get the centroid of the cell which intersects our line
        func.ST_Centroid(
            # Type coerce the return value so we van access the `geom` and
            # `val` attributes
            type_coerce(
                func.ST_Intersection(AHNRaster.rast, line_cte.c.geom),
                RasterIntersection()
            ).geom
        ).label("geom"),
        type_coerce(
            func.ST_Intersection(AHNRaster.rast, line_cte.c.geom),
            RasterIntersection()
        ).val.label("val")
    ).filter(
        func.ST_Intersects(AHNRaster.rast, line_cte.c.geom)
    ).cte(name="cells")

    height_data_cte = db.session.query(
        func.ST_Transform(
            func.ST_SetSrid(func.ST_MakePoint(
                func.ST_X(cells_cte.c.geom), func.ST_Y(cells_cte.c.geom),
            ), 28992),
            4326
        ).label("point"),
        # Select value separately instead of a Point with Z value because
        # geoalchemy and shapely do not really play nicely with higher order
        # geometries
        cells_cte.c.val.label("val"),
        line_cte
    ).order_by(func.ST_X(cells_cte.c.geom)).cte(name="height_data")

    return db.session.query(height_data_cte.c.point, height_data_cte.c.val)
