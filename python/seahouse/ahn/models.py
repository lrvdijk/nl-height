from sqlalchemy import Column, String, Integer, Text, Float
from geoalchemy2 import Geometry, Raster
from geoalchemy2.types import CompositeType

from seahouse.models import Base


class AHNUnit(Base):
    __tablename__ = 'ahn_units'

    gid = Column(Integer, primary_key=True)
    lo_x = Column(Integer)
    lo_y = Column(Integer)
    unit = Column(String(10))

    # Amersfoort / RD new projection
    geom = Column(Geometry('POLYGON', srid=28992))

    def __str__(self):
        return "AHN Unit id: {}, x: {}, y: {}".format(
            self.unit,
            self.lo_x,
            self.lo_y
        )


class AHNRaster(Base):
    __tablename__ = 'ahn_raster'

    rid = Column(Integer, primary_key=True)
    filename = Column(Text)

    rast = Column(Raster)


class RasterIntersection(CompositeType):
    """
    Make sure we can access the attributes of a PostGIS `geomval`. This type is
    for example returned when performing a ST_Intersection on a raster and a
    linestring.
    """
    typemap = {
        'geom': Geometry('LINESTRING'),
        'val': Float

    }

