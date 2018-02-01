import os
import json
import gzip

from geopy.distance import great_circle
from shapely import geometry
from geoalchemy2.shape import to_shape
from slugify import slugify

from seahouse.config import get_config


def get_json_dataset_dir():
    conf = get_config()

    return os.path.realpath(os.path.join(
        os.path.dirname(__file__), '..', '..',
        conf.get('directories', 'json.data_dir')
    ))


class Dataset:
    YMIN = -13

    def __init__(self, name, coordinates, line):
        self.name = name
        self.location_coords = coordinates
        self.line = line

        # Stores lat, long and height
        self.data = []  # type: List[dict]

    def load_from_query(self, query):
        prev = None
        for row in query:
            if row.point is not None:
                point = to_shape(row.point)

                # The raster data in the database only exists for land, if we
                # encounter water then the distance between two points will be
                # large. We then insert two artificial points at YMIN, to make
                # sure the drawing with D3.js is correct.
                curr = (point.y, point.x)
                if prev and great_circle(curr, prev).meters > 5000:
                    self.data.append({
                        'long': prev[1] + 0.00001,
                        'lat': prev[0],
                        'height': self.YMIN
                    })
                    self.data.append({
                        'long': point.x - 0.00001,
                        'lat': point.y,
                        'height': self.YMIN
                    })

                self.data.append({
                    'long': point.x, 'lat': point.y, 'height': row.val
                })

                prev = (point.y, point.x)

    def save(self):
        slug = slugify(self.name)
        datadir = os.path.join(get_json_dataset_dir(), slug)

        if not os.path.isdir(datadir):
            os.makedirs(datadir)

        metadata_file = os.path.join(datadir, 'metadata.json')
        dataset_file = os.path.join(datadir, 'dataset.json.gz')

        with open(metadata_file, "w") as f:
            metadata = {
                'type': 'Feature',
                'geometry': geometry.mapping(self.line),
                'properties': {
                    'name': self.name,
                    'location': self.location_coords
                }
            }
            json.dump(metadata, f, indent=2)

        with gzip.open(dataset_file, "wt") as f:
            json.dump({
                'data': self.data
            }, f, indent=2)

        return metadata_file, dataset_file
