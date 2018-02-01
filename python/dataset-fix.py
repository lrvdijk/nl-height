import json
import gzip
import argparse

from geopy.distance import great_circle

from seahouse.datasets import Dataset


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Fix data spacing when encountered water"
    )

    parser.add_argument(
        '-o', '--output',
        help="Output file "
    )

    parser.add_argument(
        'dataset', type=str,
        help="The dataset to fix"
    )

    args = parser.parse_args()

    print("Loading existing dataset...")
    with gzip.open(args.dataset, "rt") as f:
        data = json.load(f)

    prev = None
    new_data = []
    for i, loc in enumerate(data['data']):
        curr = (loc['lat'], loc['long'])

        if prev and great_circle(prev, curr).meters > 5000:
            print("Fixing space between", prev, "and", curr)

            new_data.append({
                'long': prev[1] + 0.00001,
                'lat': prev[0],
                'height': Dataset.YMIN
            })

            new_data.append({
                'long': loc['long'] - 0.00001,
                'lat': loc['lat'],
                'height': Dataset.YMIN
            })

        new_data.append(loc)
        prev = curr

    print("Writing output...")
    with gzip.open(args.output, "wt") as f:
        json.dump({
            'data': new_data
        }, f, indent=2)
    print("Done")
