import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import utilslib


config = utilslib.load_config()['mail-server']


def send(recipient, subject, text):
    sender = config['from']
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    rcpt = [recipient]
    part = MIMEText(text)
    msg.attach(part)
    s = smtplib.SMTP(config['smtp'])
    s.sendmail(sender, rcpt, msg.as_string())
    s.quit()

