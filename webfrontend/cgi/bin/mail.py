import logging
import smtplib
import base64
from ConfigParser import ConfigParser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders

class Email(object):
    def __init__(self):
        """Creates an object for an Email smtp connection. These methods are implemented:
        SendMsg(subject, body)
        SendAttachment(subject, body, file)"""
        logging.basicConfig(filename='/opt/loxberry/log/plugins/synology/synology.log',level=logging.INFO,format='%(asctime)s: %(message)s ')
        cfg = ConfigParser()
        cfg.read("/opt/loxberry/config/plugins/synology/plugin.cfg")
        self.email_user = cfg.get("EMAIL", "USER")
        self.email_pwd = cfg.get("EMAIL", "PWD")
        self.mail_to = cfg.get("DISKSTATION", "NOTIFICATION")
        self.smtp_server = cfg.get("EMAIL", "SMTP")
        self.smtp_port = int(cfg.get("EMAIL", "SMTP_PORT"))

    def GetVars(self):
        """print out all variables used in this class"""
        print self.email_user
        print self.email_pwd
        print self.mail_to
        print self.smtp_server
        print self.smtp_port
        
    def ServerConnect(self, msg):
        """makes the connection to the smtp server and sends the mail"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, base64.b64decode(self.email_pwd))
            server.sendmail(self.email_user, self.mail_to, msg)
            server.quit()
            return True
        except:
            logging.info("<ERROR> SMTP server connection failed")
            return False

    def SendMsg(self, subj, body):
        """Send Email as text message"""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subj
            msg['From'] = self.email_user
            msg['To'] = self.mail_to
            response = self.ServerConnect(msg.as_string())
            if (response == True):
                return True
            else:
                return False
        except:
            logging.info("<ERROR> mail not sent")
            return False

    def SendAttachment(self, subj, body, file):
        """Send Email with attachment"""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subj 
            msg['From'] = self.email_user
            msg['To'] = self.mail_to
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(file, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename=%s" % file)
            msg.attach(part)
            response = self.ServerConnect(msg.as_string())
            if (response == True):
                return True
            else:
                return False
        except e:
            logging.info("<ERROR> mail not sent")
            return False

