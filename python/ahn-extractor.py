import os
import argparse
import zipfile
import traceback

from seahouse.config import load_config


def extract(filename):
    directory = os.path.dirname(filename)

    with zipfile.ZipFile(filename) as zf:
        for file in zf.infolist():
            zf.extract(file, directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Helper script to extract all AHN zipped datasets"
    )

    parser.add_argument('-c', '--config', required=False, default=None,
                        help="Specify other configuration file.")

    args = parser.parse_args()

    conf = load_config(args.config if args.config else None)
    data_dir = os.path.realpath(os.path.join(
        os.path.dirname(__file__), '..',
        conf.get('directories', 'ahn.units_dir')
    ))

    for file in os.listdir(data_dir):
        path = os.path.join(data_dir, file)
        if os.path.isfile(path) and path.endswith('.zip'):
            print("Extracting", path)

            try:
                extract(path)
            except zipfile.BadZipfile:
                print("Could not extract", path, " - removing file")
                traceback.print_exc()

                os.remove(path)
