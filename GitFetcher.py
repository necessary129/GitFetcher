#!/usr/bin/env python3

#  GitFetcher: Pulls from GitHub automatically
#  Copyright (C) 2015 Muhammed Shamil K
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, download it from here: https://noteness.cf/GPL.txt
#  PDF: https://noteness.cf/GPL.pdf

from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import select
import cgi
import json
import urllib.parse
import socket
import subprocess
import sqlite3
import datetime

connect_db = lambda : sqlite3.connect('data.sqlite3')

def init_db():
    with connect_db() as f:
        query = 'CREATE TABLE IF NOT EXISTS repo (name text, dir text)'
        f.execute(query)

init_db()

httpd = None

import config

host = config.HOST
port = config.PORT 

gitli = ["127.0.0.", "::ffff:192.30.252.", "::ffff:192.30.253.", 
"::ffff:192.30.254.", "::ffff:192.30.255.", "::ffff:204.232.175.", 
"192.30.252.", "192.30.253.", "192.30.254.", "192.30.255.", "204.232.175."]

gitend = [".github.com", ".cloud-ips.com"]

def logger(fil):
    def log(string):
        with open(fil,'a') as f:
            f.write("[{0}] {1}\n".format(datetime.datetime.now(),string))
    return log

messages = logger('messages.log')
errors = logger('errors.log')
verbose = logger('verbose.log')

def message(string):
    messages(string)
    verbose(string)

def get_repo_dir(repo):
    with connect_db() as s:
        cursor = s.execute('SELECT dir from repo where name=?',[repo])
        li = cursor.fetchall()
    return li

def pull(direct):
    success = True
    string = ''
    global init_dir
    commands = ["git fetch",
                "git rebase --stat --preserve-merges"]
    os.chdir(direct)
    for command in commands:
        child = subprocess.Popen(command.split(),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        (out, err) = child.communicate()
        string += out+'\n'+err+'\n\n\n'
        ret = child.returncode
        if ret != 0:
            success = False
    os.chdir(init_dir)
    return (success,string.strip())


def main():
    print('Starting on {0}:{1}'.format(host,port))
    global httpd
    server_address = (str(host),int(port))
    httpd = HTTPServer(server_address, GitHandler)
    httpd.serve_forever()

def process(form):
    repo = form['repository']['full_name']
    dirs = get_repo_dir(repo)
    if not dirs:
        message("No directory found for {0}".format(repo))
        return
    message("Directories found: Repo: '{0}' Directories: {1}".format(repo, ", ".join(dirs)))
    for direct in dirs:
        message("Pulling in {0}".format(direct))
        ret, string = pull(direct)
        if ret:
            message("Pulling Completed successfully")
        else:
            message("Pulling failed")
            verbose("Detailed:")
            verbose(string)

class GitHandler(BaseHTTPRequestHandler):
    def_res = """You aren't supposed to be here?
    Or are you? Just go away, please....""".encode('utf8')

    unauth_res = """Are you sure you are GitHub, 'coz i don't think so
    Find a better job, don't annoy me, pls...""".encode('utf8')
    server_version = 'GitHandler/0.2'
    def is_github(self):
        if not 'GitHub' in self.headers.get('User-agent',''):
            return False
        for start in gitli:
            if self.client_address[0].startswith(start):
                return True
        resolved = socket.getfqdn(self.client_address[0])
        for end in gitend:
            if resolved.endswith(end):
                return True
        return False

    def finalize(self, code, string):
        if not isinstance(code, int):
            code = int(code)
        if not isinstance(string, bytes):
            string = str(string)
            string = string.encode('utf8')
        self.send_response(code)
        self.send_header('Content-Type','text/html')
        self.send_header('Content-Length',str(len((string))))
        self.end_headers()
        self.wfile.write(string)

    def do_POST(self):
        event = self.headers.get('X-Github-Event', '').lower()
        if not event:
            self.finalize(401,self.def_res)
            return
        if not self.is_github():
            self.finalize(401,self.unauth_res)
            return
        if event == 'ping':
            self.finalize(200,'Aah Ping. Thanks!')
            return
        leng = int(self.headers.get('Content-Length','0'))
        if self.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,
                environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type']})['payload'].value
            form = form.replace('\\','')
        else:
            read = self.rfile.read(leng).decode('utf8')
        if self.headers['Content-Type'] == 'application/json':
            form = read
        form = json.loads(form)
        self.finalize(200,'Thank you!')
        if event == 'push':
            msg = 'Recieved Payload for the commit {0} of {1} by {2} ({3})'.format(
            form['head_commit']['id'],form['repository']['full_name'],
            form['head_commit']['committer']['username'],form['head_commit']['committer']['name'])
            message(msg)
            process(form)
        else:
            msg = 'Recieved {0} event'.format(event)
            message(msg)


    def do_GET(self):
        self.finalize(401,self.def_res)

if __name__ == '__main__':
#    chthr = Thread(target=check_change)
#    chthr.start()
    main()