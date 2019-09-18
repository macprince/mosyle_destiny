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
import xlsxwriter

# Set up argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug",
                    help="Turns debug logging on",
                    action="store_true")
parser.add_argument("--config",
                    help="Specify path to config.json",
                    default=os.path.join(sys.path[0],"config.json"))
parser.add_argument("csv",
                    help="Path to the Mosyle export CSV file")
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

# Load in config file
config = os.path.abspath(args.config)
try:
    with open(config) as config_file:
        settings = json.load(config_file)
except IOError:
    logging.error("No config.json file found! Please create one!")
    sys.exit(2)

# Read in config
destiny_config = settings['server_info']

def read_serials_from_csv(csv_file):
    serials = []
    with open(csv_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['Asset Tag'] == "":
                serials.append(row['Serial Number'])
    return serials

def get_device_data(serials, host, user, password, db):
    if len(serials) == 1:
        barcode_cmd = "SELECT SerialNumber, CopyBarcode FROM CircCatAdmin.CopyAssetView WHERE SerialNumber = '{0}'".format(serials[0])
    else:
        barcode_cmd = "SELECT SerialNumber, CopyBarcode FROM CircCatAdmin.CopyAssetView WHERE SerialNumber IN {}".format(tuple(serials))
    db_host = host
    db_user = user
    db_password = password
    db_name = db
    try:
        with pytds.connect(db_host, database=db_name, user=db_user,
                           password=db_password, as_dict=True) as conn:
            logging.debug("Server Connection Success")
            with conn.cursor() as cur:
                cur.execute(barcode_cmd)
                logging.debug("Lookup Command Executed")
                devicedata = (cur.fetchall())
                logging.debug("Date retrieved, closing connection")

    except pytds.tds.LoginError:
        logging.error("Unable to connect to server! Connection may have timed out!")
        sys.exit(2)
    cur.close()
    conn.close()

    return devicedata

def write_mosyle_xlsx(devicedata):
    xlsx_file = os.path.join(os.path.dirname(os.path.abspath(args.csv)),'MosyleImport.xlsx')
    workbook = xlsxwriter.Workbook(xlsx_file)
    worksheet = workbook.add_worksheet('Devices')
    row = 0
    col = 0

    headers=["Serial Number","Device Name","Lock Message","Asset Tag","Tags"]
    for header in headers:
        worksheet.write(0,col,header)
        col += 1
    row += 1
    for device in devicedata:
        worksheet.write(row,0,device['SerialNumber'])
        worksheet.write(row,3,device['CopyBarcode'])
        row += 1

    workbook.close()

def main():
    if args.csv:
        csv_file = os.path.abspath(args.csv)
        serials = read_serials_from_csv(csv_file)

        if serials != []:
            data = get_device_data(serials,
                                   destiny_config["server"],
                                   destiny_config["user"],
                                   destiny_config["password"],
                                   destiny_config["database"])

            logging.debug("Got device data from server!\n%s", data)
            if not data:
                logging.error("No data")
            else:
                write_mosyle_xlsx(data)
    sys.exit(0)

if __name__ == '__main__':
    main()
