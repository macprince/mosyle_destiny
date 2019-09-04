#!/usr/local/bin/python3
import csv
import os
import sys

serials = []

with open(os.path.join(sys.path[0], 'devices_info_5d704946e0f45.csv'), mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        if row['Asset Tag'] == "":
            serials.append(row['Serial Number'])
