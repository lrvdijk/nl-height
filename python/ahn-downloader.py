import os
import argparse

from seahouse import db
from seahouse.config import load_config
from seahouse.ahn import datasets, models


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Preprocess AHN data"
    )

    parser.add_argument(
        '-c', '--config', required=False, default=None,
        help="Specify a different configuration file to use "
             "instead of the default one."
    )

    args = parser.parse_args()

    conf = load_config(args.config if args.config else None)
    db.init()

    units = list(db.session.query(models.AHNUnit))
    print(len(units), "AHN units in total")

    units_dataset_dir = os.path.realpath(os.path.join(
        os.path.join(os.path.dirname(__file__), '..'),
        conf.get('directories', 'ahn.units_dir')
    ))

    if not os.path.isdir(units_dataset_dir):
        os.makedirs(units_dataset_dir)

    for i, unit in enumerate(units):
        filename = "ahn2_5_{id}.tif.zip".format(id=unit.unit)
        path = os.path.join(units_dataset_dir, filename)

        print(i+1, "/", len(units), "dataset", unit.unit)

        if os.path.exists(path):
            print("\t file exists, skipping")
        else:
            datasets.download_dataset(unit.unit, units_dataset_dir)
