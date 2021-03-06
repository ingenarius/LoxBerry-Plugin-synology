import requests
import logging
import urllib
import smtplib
import base64
from tbot import MyTelegramBot
from mail import Email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from subprocess import call,STDOUT

class DiskStation(object):
    def __init__(self, ds_user, ds_pwd, ds_ip, ds_port, email, installfolder="/opt/loxberry"):
        """Creates an object for a Synology DiskStation using the official Web API v2.0.
        #######################################################
        #     Synology DISK STATION
        #######################################################
        # create object for DiskStation functions
        # change data according to your setup in proxy.py
        #######################################################
        """
        self.user = ds_user         # user to manage DiskStation
        self.installfolder = str(installfolder)  # loxberry install folder / base
        try:
            self.passwd = base64.b64decode(ds_pwd)        # password
            logging.basicConfig(filename='%s/log/plugins/synology/synology.log' % installfolder,level=logging.INFO,format='%(asctime)s: %(message)s ')
        except:
            logging.info("<ERROR> password decoding not possible!")
            logging.basicConfig(filename='%s/log/plugins/synology/synology.log'% installfolder,level=logging.DEBUG,format='%(asctime)s: %(message)s ')
            self.passwd = ""
        self.ip = ds_ip             # IP of the DiskStation
        self.port = ds_port         # TCP Port to connect to the DiskStation
        self.mail = email           # email for notifications / snapshots
        self.api_url = "http://%s:%s/webapi/" % (self.ip, self.port)
        self.auth_url = "http://%s:%s/webapi/auth.cgi?" % (self.ip, self.port)
        


    def Alive(self):
        """Check if Diskstation is alive on the network. Return 'True' or 'False' """
        try:
            alive = call("ping -c 1 %s" % self.ip, shell=True, stdout=open('/dev/null', 'w'), stderr=STDOUT)
            if alive == 0:
                return True
            else:
                return False
        except:
            logging.info("<ERROR> exeption in \"Alive\"")
            return False

    def Execute(self, command):
        """Execute Web API command. Return 'True' or 'False' """
        if self.Alive() == True:    # host is alive
            exe = requests.get(command)
            try:
                logging.debug("<INFO> execution of command \"%s\" was OK!" % command)  
                return exe.json().get('success')
            except:
                logging.info("<ERROR> command not executed!")
                return False
        else:   # host is not reacable
            logging.info("<ERROR> DS not alive!")
            return False

    def Login(self):
        """login to Diskstation and return 'True' or 'False' """
        try:
            login_url = self.auth_url + 'api=SYNO.API.Auth&method=Login&version=2&account=%s&passwd=%s&session=SurveillanceStation&format=sid' % (self.user, self.passwd)

            if self.Alive() == True:    # host is alive
                self.login = requests.get(login_url)
                self.sid = self.login.json().get('data').get('sid')
                return True
            else:   # host is not reachable
                self.sid = ''
                logging.info("<ERROR> DS not alive!")
                return False
        except:
            logging.info("<ERROR> login exception...")
            self.sid = ''
            return False

    def GetSid(self):
        """get session ID"""
        return self.sid

    def Logout(self):
        """Logout of Diskstation. Return 'True' or 'False' """
        try:
            logout_url = self.auth_url + 'api=SYNO.API.Auth&method=Logout&version=2&session=SurveillanceStation&_sid=%s' % (self.sid)
            return self.Execute(logout_url)
        except:
            logging.info("<ERROR> logout not possible!")
            return False

    def GetCams(self):
        """Get a list of all installed cameras and return (ID, Vendor, Type)"""
        try:
            list_url = self.api_url + 'entry.cgi?version="8"&streamInfo=true&basic=true&api=SYNO.SurveillanceStation.Camera&method=List&_sid=%s' % (self.sid)
            #logging.info(list_url)
            if self.Alive() == True:    # host is alive
                self.cam_list = requests.get(list_url)
                cam_ids = ""
                if self.cam_list.json().get('success') == True:
                    #for c in self.cam_list.json().get('data').get('cameras'):
                    #    if len(self.cam_list.json().get('data').get('cameras')) == 1:
                    #        cam_ids += str(c.get('id'))
                    #    else:
                    #        cam_ids += str(c.get('id')) + ", "
                        #c_id = str(c.get('id'))
                        #c_vendor = str(c.get('vendor'))
                        #c_model = str(c.get('model'))
                        #print(c_id + ": " + c_vendor + " - " + c_model)
                    #return "OK"
                    return self.cam_list
                else:   # cam_list is empty
                    logging.info("<ERROR> cam list is empty")
                    return ''
            else:   # host is unreachable
                logging.info("<ERROR> host is unreachable")
                return ''
        except:
            logging.info("<ERROR> something went wrong!")
            return ''

    def MotionDetectionOn(self, cam_id):
        """Turn on Motion Detection on all installed Cams. Return 'True' or 'False' """
        try:
            url_param = 'entry.cgi?source=1&camId=%s&version="1"&api="SYNO.SurveillanceStation.Camera.Event"&method="MDParamSave"&keep=true&_sid=%s' \
                % (str(cam_id), self.sid)    # parameters of this API function
            self.on_url = self.api_url + url_param
            return self.Execute(self.on_url)
        except:
            logging.info("<ERROR> Motion Detection NOT enabled")
            return False

    def MotionDetectionOff(self, cam_id):
        """Turn off Motion Detection on all installed Cams. Return 'True' or 'False' """
        try:
            url_param = 'entry.cgi?source=-1&camId=%s&version="1"&api="SYNO.SurveillanceStation.Camera.Event"&method="MDParamSave"&keep=true&_sid=%s' \
                % (str(cam_id), self.sid)    # parameters of this API function
            self.off_url = self.api_url + url_param
            return self.Execute(self.off_url)
        except:
            logging.info("<ERROR> Motion Detection NOT disabled")
            return False

    def StartRec(self, cam_id):
        """Start recording of camera. Argument is the ID of the camera. Return 'True' or 'False' """
        try:
            url_param = 'entry.cgi?api=SYNO.SurveillanceStation.ExternalRecording&method=Record&version=1&cameraId=%s&action=start&_sid=%s' % (str(cam_id), self.sid)
            self.startrec_url = self.api_url + url_param
            return self.Execute(self.startrec_url)
        except:
            logging.info("<ERROR> Recording NOT started")
            return False

    def StopRec(self, cam_id):
        """Stop recording of camera. Argument is the ID of the camera. Return 'True' or 'False'"""
        try:
            url_param = 'entry.cgi?api=SYNO.SurveillanceStation.ExternalRecording&method=Record&version=1&cameraId=%s&action=stop&_sid=%s' % (str(cam_id), self.sid)
            self.stoprec_url = self.api_url + url_param
            return self.Execute(self.stoprec_url)
        except:
            logging.info("<ERROR> Recording NOT stopped")
            return False

    def MailEnable(self):
        """Enable mail notifications via predifined (Web GUI) settings. REQUIRES administrative privileges on the diskstation!"""
        try:
            url_param = 'entry.cgi?version="1"&mailEnable=true&api="SYNO.SurveillanceStation.Notification.Email"&method="SetSetting"&_sid=%s' % (self.sid)
            self.mail_on_url = self.api_url + url_param
            return self.Execute(self.mail_on_url)
        except:
            logging.info("<ERROR> Mail notifications NOT enabled")
            return False

    def MailDisable(self):
        """Disable mail notifications. REQUIRES administrative privileges on the diskstation!"""
        try:
            url_param = 'entry.cgi?version="1"&mailEnable=False&api="SYNO.SurveillanceStation.Notification.Email"&method="SetSetting"&_sid=%s' % (self.sid)
            self.mail_off_url = self.api_url + url_param
            return self.Execute(self.mail_off_url)
        except:
            logging.info("<ERROR> Mail notifications NOT disabled")
            return False

    def GetSnapshot(self, cam_id):
        """Get snapshot from camera and store it as /tmp/snapshot.jpg"""
        try:
            url_param = 'entry.cgi?version=9&id=%s&api="SYNO.SurveillanceStation.Camera"&method="GetSnapshot"&profileType=0&_sid=%s' % (str(cam_id), self.sid)
            url = self.api_url + url_param
            snapshot = "%s/data/plugins/synology/snapshot.jpg" % self.installfolder
            with open(snapshot, 'wb') as handle:
                response = requests.get(url, stream=True)
                logging.info(response)
                if not response.ok:
                    err_msg = "<ERROR> fetching snapshot: ", response
                    logging.info(err_msg)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
                logging.info("<INFO> snapshot fetched!")
            return True
        except:
            logging.info("<ERROR> something went wrong!")
            return False

    def SendSnapshot(self, send_option):
        """Send snapshot /tmp/snapshot.jpg 
        send options are:
            1   ...	Telegram bot
            2   ...	Email"""
        if send_option == 1:
            try:
                bot = MyTelegramBot()
                response = bot.send_photo("%s/data/plugins/synology/snapshot.jpg" % self.installfolder)
                if response == True:
                    logging.info("<INFO> Photo sent to Telegram!")
                    return True
                else:
                    logging.info("<ERROR> Photo NOT sent to Telegram!")
                    return False
            except:
                return False
        elif send_option == 2:
            try:
                m = Email()
                m.SendAttachment("Snapshot", "Greetings from your Loxberry", "%s/data/plugins/synology/snapshot.jpg" % self.installfolder)
            except:
                logging.info("<INFO> sending email not implemented yet")
                return False
        else:
            logging.info("<ERROR> no valid send option!")
            return False
