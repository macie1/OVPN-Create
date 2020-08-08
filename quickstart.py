from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
from apiclient import errors
import qrcode
from sys import argv
######## if needed add "duplicate-cn" to server.conf
######## for clients to communicate add "client-to-client" to server.conf
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    user = argv[1]
    with open(f"/etc/openvpn/gauth/{user}") as f:
        secret = f.readline()
    data = f"otpauth://totp/VPN%20server?secret={secret}&issuer=HackerU"
    filename = f"{user}.png"
    img = qrcode.make(data)
    img.save(filename)

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    message = """\
<html>
  <head></head>
  <body>
    <p>The VPN profile file</p>
    <p>Please remove this email after using the QR code.</p>
  </body>
</html>
"""
    x = CreateMessageWithAttachment("me", "stankiewiczmaciek179@gmail.com", "tests of API", message,"C:\\Users\\Mati\\Desktop\\projects\\VPN\\", "test.png")
    SendMessage(service, "me", x)

def SendMessage(service, user_id, message):
    try:
        message = (service.users().messages().send(
            userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as err:
        print(f'An error occurred: {err}')


def CreateMessageWithAttachment(sender, to, subject, message_text, file_dir, filename):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text, "html")
    message.attach(msg)

    path = os.path.join(file_dir, filename)
    content_type, encoding = mimetypes.guess_type(path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(path, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(path, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(path, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(path, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

if __name__ == '__main__':
    main()
