#!/usr/local/bin/python3
import csv
import os
import sys

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
        csv_path = os.path.abspath(sys.argv[1])

    sys.exit(0)

if __name__ == '__main__':
    main()
