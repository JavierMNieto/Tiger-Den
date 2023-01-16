#!/usr/bin/env python

import argparse
import os

SRC_DIR = "tigerden"
MANAGE = os.path.join(SRC_DIR, "manage.py")
FIXTURES_DIR = os.path.join(SRC_DIR, "fixtures")
FIXTURES = [
    "attribute_option_groups.json",
    "attribute_options.json",
    "options.json",
    "product_classes.json",
    "products.json",
    "categories.json",
    "product_categories.json",
    "product_images.json",
    "stock_records.json",
    "account_types.json",
    "accounts.json"
]

# windows activate virtualenv
windows_activate = os.path.abspath("venv/Scripts/activate.bat")


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="commands")

    # initialize db
    db_parser = subparsers.add_parser("initdb", help="initialize database")
    db_parser.set_defaults(func=initialize_db)

    # runserver
    run_parser = subparsers.add_parser("runserver", help="runserver")
    run_parser.set_defaults(func=runserver)

    return parser.parse_args()


def runserver(args):
    os.system(f"python {MANAGE} runserver")


def initialize_db(args):
    os.system(f"python {MANAGE} migrate --run-syncdb")
    os.system(f"python {MANAGE} createsuperuser")
    for fixture in FIXTURES:
        fixture_path = os.path.join(FIXTURES_DIR, fixture)
        os.system(f"python {MANAGE} loaddata {fixture_path}")


if __name__ == "__main__":
    args = parse_arguments()
    args.func(args)
