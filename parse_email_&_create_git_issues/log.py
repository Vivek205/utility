import email
import json
import poplib
import time
import pytz
from dateutil.parser import parse

import requests


class Issue:
    def __init__(self):
        self.username = 'prashantramangupta'
        self.password = 'xxxxxxx'
        self.REPO_OWNER = 'xxxxxxx'
        self.assignee = 'xxxxx#'
        self.REPO_NAME = 'beta-bugs'
        self.SERVER = "pop.gmail.com"
        self.GUSER = "xyz@gmail.com"
        self.GPASSWORD = "xxxxxxxxxxxxxxxxxxx"
        self.threshold_date = '2019-02-06 13:00:00'  # after this time
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.th_epoch_dt = time.mktime(time.strptime(self.threshold_date, self.dt_format))
        self.EMAIL = 'abc@sgmail.com'

    def make_github_issue(self, title, body=None, assignee=None, milestone=None, labels=None):
        url = 'https://api.github.com/repos/%s/%s/issues' % (self.REPO_OWNER, self.REPO_NAME)
        session = requests.Session()
        session.auth = (self.username, self.password)
        issue = {'title': title,
                 'body': body,
                 'assignee': assignee,
                 'milestone': milestone,
                 'labels': labels}
        r = session.post(url, json.dumps(issue))
        if r.status_code == 201:
            print('successfully created issue ', title)
        else:
            print('could not create issue ', title)
            print('Response:', r.content)

    def fetch_email_body(self, b):
        body = ""
        for part in b.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)
                break
            else:
                body = b.get_payload(decode=True)
        return body

    def listener(self):
        print('connecting to ' + self.SERVER)
        server = poplib.POP3_SSL(self.SERVER)
        server.user(self.GUSER)
        server.pass_(self.GPASSWORD)
        resp, items, octets = server.list()
        print('no. of emails', len(items))
        count = 0
        for item in items:
            mail_no = int((item.decode('utf-8')).split()[0])
            if mail_no >= 0:
                print(mail_no)
                id, size = str.split(items[count].decode('utf-8'))
                resp, text, octets = server.retr(id)
                rw_str = ''.join(rec.decode('utf-8') + "\n" for rec in text)
                b = email.message_from_string(rw_str)
                ccc = b['to']
                dt_str = parse(b['Date']).astimezone(pytz.utc)
                dt_str = str(dt_str).split("+")[0].strip()
                print(dt_str, ccc)
                mail_date = time.mktime(time.strptime(dt_str, self.dt_format))
                print(mail_date, ccc)

                if mail_date > self.th_epoch_dt and self.EMAIL in ccc:
                    bbb = b['from']
                    body = (self.fetch_email_body(b)).decode("utf-8")
                    body = body.replace('\n', '<br/>')
                    title = b['Subject']
                    body = "Description from " + str(bbb) + ": <br/>" + str(body)
                    payload = {
                        'title': title,
                        'body': body,
                        'date': mail_date
                    }
                    print(payload)

                    # posting on git hub
                    # please check self.threshold_date before enabling
                    # self.make_github_issue(payload['title'], payload['body'], self.assignee, None,
                    #                       ['beta'])

                count = count + 1;


if __name__ == '__main__':
    obj = Issue()
    obj.listener()
