#!/usr/bin/env python3
'''
Find devices in Mosyle Manager export CSV that don't have asset tags set, look those serial numbers up in Destiny, then write a XLSX import file to import back into Mosyle.
'''
# Standard Imports
import json
import argparse
import subprocess
import logging
import os
import sys
import re
# Custom Imports
import pytds
import csv

# Set up argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug",
                    help="Turns Debug Logging On.",
                    action="store_true")
# parser.add_argument("--config",
#                     help="Specify path to config.json",
#                     default=os.path.join(sys.path[0],"config.json"))

args = parser.parse_args()

# Set up logging
level = logging.INFO
if args.debug:
    level = logging.DEBUG
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p',
                    level=level,
                    filename=os.path.join(sys.path[0],'mosyle_destiny.log'))
stdout_logging = logging.StreamHandler()
stdout_logging.setFormatter(logging.Formatter())
logging.getLogger().addHandler(stdout_logging)

def read_serials_from_csv(csv_file):
    serials = []
    with open(csv_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['Asset Tag'] == "":
                serials.append(row['Serial Number'])
    return serials






def main():
    if len(sys.argv) == 2:
        csv_file = os.path.abspath(sys.argv[1])
        serials = read_serials_from_csv(csv_file)

    sys.exit(0)

if __name__ == '__main__':
    main()
