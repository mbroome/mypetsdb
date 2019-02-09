#!/usr/bin/env python
import json

content = open('/etc/config/mypetsdb.json', 'r').read()
data = json.loads(content)
mypetsdb = data['db']['mypetsdb']
parts = mypetsdb.split('/')
username = parts[2][:parts[2].find(':')]
password = parts[2][parts[2].find(':') + 1:parts[2].find('@')]
host = parts[2][parts[2].find('@') + 1:]

print '''
[client]
user=%s
password=%s
host=%s
database=mypetsdb
''' % (username, password, host)

