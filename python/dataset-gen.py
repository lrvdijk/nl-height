import argparse

from shapely import geometry

from seahouse import db, location
from seahouse.datasets import Dataset
from seahouse.config import load_config
from seahouse.ahn import datasets, profiles


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Preprocess AHN data"
    )

    parser.add_argument(
            '-c', '--config', required=False, default=None,
            help="Specify a different configuration file to use "
                 "instead of the default one."
    )

    parser.add_argument(
        'location', type=str, help="The location which determines the y "
                               "position in the Netherlands as reference for "
                               "generation of the height data"
    )

    args = parser.parse_args()

    conf = load_config(args.config if args.config else None)
    db.init()

    print("Generating dataset for location", args.location)
    coords = location.get_coordinates(args.location)

    print("Determine x1 and x2 for intersection line")
    bbox = datasets.get_geometry_extent()
    x_min = bbox[0]
    x_max = bbox[2]

    # Create horizontal line through the Netherlands
    line = geometry.LineString([
        (x_min, coords[1]),
        (x_max, coords[1])
    ])

    print("Generate elevation profile")
    elevation_query = profiles.generate_elevation_profile(line)
    dataset = Dataset(args.location, coords, line)

    dataset.load_from_query(elevation_query)

    print("Save data to JSON")
    files = dataset.save()

    print("Data saved to:")
    print(files[0])
    print(files[1])
