from synology import DiskStation
from ConfigParser import ConfigParser
from time import sleep
import socket
import logging

def main():
    """loxberry plugin for synology surveillance station API functions:
        MailEnable:			enable mail notifications
        MailDisable:		disable mail notifications
        StartRec: 			start recording for one camera
        StopRec:			stop recording for one camera
        MotionDetectionOn:	enable motion detection for all cameras
        MotionDetectionOff:	disable motion detection for all cameras"""
    # creating log file and set log format
    logging.basicConfig(filename='/opt/loxberry/log/plugins/synology/synology.log',level=logging.INFO,format='%(asctime)s: %(message)s ')
    logging.info("<INFO> initialise logging...")
    # open config file and read options
    try:
        cfg = ConfigParser()
        global_cfg = ConfigParser()
        cfg.read("/opt/loxberry/config/plugins/synology/plugin.cfg")
        global_cfg.read("/opt/loxberry/config/system/general.cfg")
    except ConfigParser.ParsingError, err:
        msg = "Error parsing config file: %s" % str(err)
        logging.info(msg)

    # define UDP server
    UDP_IP = global_cfg.get("NETWORK", "IPADDRESS")
    UDP_PORT = int(cfg.get("SERVER", "PORT"))
    try:
        # start the server listening on UDP socket
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        sock.bind( (UDP_IP,UDP_PORT) )
    except:
        logging.info("<ERROR> failed to bind socket!")
        
    # initialise variable(s)
    result = False
    DS_USER = cfg.get("DISKSTATION", "USER")
    DS_PWD = cfg.get("DISKSTATION", "PWD")
    DS_HOST = cfg.get("DISKSTATION", "HOST")
    DS_PORT = cfg.get("DISKSTATION", "PORT")
    EMAIL = cfg.get("DISKSTATION", "NOTIFICATION")
    CIDS = cfg.get("DISKSTATION", "CIDS")
    try:
        SENT_VIA = int(cfg.get("DISKSTATION", "SENT_VIA"))
    except:
        SENT_VIA = 0
    MINISERVER = global_cfg.get("MINISERVER1", "IPADDRESS")
    INSTALLFOLDER = global_cfg.get("BASE", "INSTALLFOLDER")
    logging.info("<INFO> DiskStation - " + DS_HOST + ", " + DS_PORT + ", " + DS_USER + ", " + EMAIL)
    logging.info("<INFO> Camera IDs - " + CIDS)
    logging.info("<INFO> Miniserver - " + MINISERVER)	

    while True:
        data, addr = sock.recvfrom( 1024 ) # read data with buffer size of 1024 bytes
        logging.info("<INFO> received message from %s: %s" % (addr[0], data))

        if (addr[0] == MINISERVER):     # only the miniserver is allowed to send commands
            # create DS object and login
            ds = DiskStation(DS_USER, DS_PWD, DS_HOST, DS_PORT, EMAIL, INSTALLFOLDER)
            s = ds.Login()
            # on login error the answer will be "False"
            if ( s == False ):
                continue
            # StartRec sends also the ID of the camera
            elif ( str(data).__contains__("StartRec:") ):
                logging.info("<INFO> %s: executing..." % data)
                response = ds.StartRec(data.split(":")[1])
            # StopRec sends also the ID of the camera
            elif ( str(data).__contains__("StopRec:") ):
                logging.info("<INFO> %s: executing..." % data)
                response = ds.StopRec(data.split(":")[1])
            # Motion detection enable/disable for all cameras
            elif ( str(data).__contains__("MotionDetection") ):
                for c in CIDS.split(","):
                    #logging.info("camera id: %s" % str(c))
                    sleep(3)        # wait before the next request will be sent
                    if ( (data == "MotionDetectionOn") and c != 0):
                        logging.info("<INFO> %s: executing for camera ID %s ..." % (data, str(c)))
                        response = ds.MotionDetectionOn(c)
                    elif ( (data == "MotionDetectionOff") and c != 0):
                        logging.info("<INFO> %s: executing for camera ID %s ..." % (data, str(c)))
                        response = ds.MotionDetectionOff(c)
                    else:
                        return
                sleep(3)        # wait before the next request will be sent
            # request does not match
            elif ( str(data).__contains__("Snapshot:") ):
                logging.info("<INFO> %s: executing..." % data)
                for i in range(1, 4):
                    response = ds.GetSnapshot(data.split(":")[1])
                    if response == True and SENT_VIA != 0:
                        response = ds.SendSnapshot(SENT_VIA)	# send snapshot via: 1 - Telegram bot, 2 - Email
                        sleep(5)
            else:
                logging.info("<INFO> \"%s\" is no valid message!" % data)
                response = False
                continue
            # log the responses
            if response == True:
                logging.info("<INFO> successful executed \"%s\" " % data)
            else:
                logging.info("<ERROR> %s not executed" % data)
            # logout from Diskstation
            ds.Logout()
        else:
            msg = "<INFO> message \"%s\" not from \"%s\" " % (data, MINISERVER)
            logging.info(msg)
            continue

if __name__ == "__main__":
    main()
