#!/usr/bin/python

from synology import DiskStation
from ConfigParser import ConfigParser
from time import sleep
import socket
import logging

def main():
    """get a list of all installed cameras"""
    # creating log file and set log format
    logging.basicConfig(filename='/opt/loxberry/log/plugins/synology/synology.log',level=logging.INFO,format='%(asctime)s: %(message)s ')
    logging.info("<INFO> initialise logging...")
    # open config file and read options
    try:
        cfg = ConfigParser()
        cfg.read("/opt/loxberry/config/plugins/synology/plugin.cfg")
    except ConfigParser.ParsingError, err:
        msg = "Error parsing config file: %s" % str(err)
        logging.info(msg)
        quit()
        
    # initialise variable(s)
    DS_USER = cfg.get("DISKSTATION", "USER")
    DS_PWD = cfg.get("DISKSTATION", "PWD")
    DS_HOST = cfg.get("DISKSTATION", "HOST")
    DS_PORT = cfg.get("DISKSTATION", "PORT")
    EMAIL = cfg.get("DISKSTATION", "NOTIFICATION")
    
    try:
        ds = DiskStation(DS_USER, DS_PWD, DS_HOST, DS_PORT, EMAIL)
        s = ds.Login()
    except:
        logging.info("<ERROR> login to DiskStation was not possible")
        quit()
    if s == True:
        cam_file = open("/opt/loxberry/data/plugins/synology/cameras.dat", "w")
        cam_list = ds.GetCams()
        if cam_list != '':
            for c in cam_list.json().get('data').get('cameras'):
                c_id = str(c.get('id'))
                c_vendor = str(c.get('vendor'))
                c_model = str(c.get('model'))
                cam_file.write(c_id + ": " + c_vendor + " - " + c_model)
        cam_file.close()
    else:
        quit()

if __name__ == "__main__":
    main()