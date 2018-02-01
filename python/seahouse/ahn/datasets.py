import os

import requests
from clint.textui import progress

from sqlalchemy import func
from shapely import geometry
from geoalchemy2.shape import from_shape, to_shape

from seahouse import db
from seahouse.ahn.models import AHNUnit

AHN_DATASET_URL_TEMPLATE = (
    "http://geodata.nationaalgeoregister.nl/ahn2/extract/ahn2_5m/ahn2_5_{id}"
    ".tif.zip"
)


def download_dataset(unit_id, output_dir):
    """
    Download the dataset for a given region of the Netherlands, specified by
    its id. To get the right id, please see the `AHNUnit` model which allows
    for spatial querying of the id's.

    :param unit_id: The AHN unit ID
    :type unit_id: str
    :param output_dir: The directory where the dataset will be saved
    :type output_dir: str

    .. seealso::
        class `AHNUnit`
    """

    url = AHN_DATASET_URL_TEMPLATE.format(id=unit_id)
    req = requests.get(url, stream=True)

    output_file = os.path.basename(url)

    with open(os.path.join(output_dir, output_file), "wb") as f:
        for chunk in progress.dots(req.iter_content(chunk_size=1024),
                                   every=32):
            if chunk:
                f.write(chunk)
                f.flush()


def get_location_unit(coordinates):
    location = geometry.Point(coordinates)
    point = from_shape(location, srid=4326)

    return db.session.query(AHNUnit).filter(
            AHNUnit.geom.ST_Contains(
                    func.ST_Transform(point, 28992)
            )
    ).first()


def get_unit_row(unit):
    return db.session.query(AHNUnit).filter_by(lo_y=unit.lo_y).order_by(
            AHNUnit.lo_x)


def get_geometry_extent():
    """
    Get the bounding box of the Netherlands in WGS-84 coordinates

    :return: Tuple with the min x, min y, max x, and max y values
    :rtype: tuple
    """
    result = db.session.query(
        func.ST_Transform(
            func.ST_SetSrid(func.ST_Extent(AHNUnit.geom), 28992),
            4326
        )
    ).first()

    return to_shape(result[0]).bounds if result[0] is not None else None

