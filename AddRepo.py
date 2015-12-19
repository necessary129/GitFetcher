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

import sqlite3
import sys
from GitFetcher import connect_db, init_db
import difflib
import os.path
from config import HOST, PORT
init_db()

after_making = """
Great!
We have set it up! But remember, you have to set up a web hook
to your server for your repo to be automatically updated

See the webhook documentation at: https://developer.github.com/webhooks/
or the one at https://developer.github.com/webhooks/creating/ if you need a quick README

Add http://<YOUR IP>:<PORT> as the url. 
You can either choose 'application/json' or 'application/x-www-form-encoded'
as the type. No Secret is needed.

FYI: Your Port is {0}{1}
""".format(PORT, " ,And your bindaddress is {0}".format(HOST) if HOST != '' else '')

def add(repo, path):
    with connect_db() as f:
        f.execute('INSERT INTO repo(name, dir) VALUES (?, ?)',[repo,path])

def ask(question,l=False):
    sys.stdout.write(question+": ")
    sys.stdout.flush()
    answer = sys.stdin.readline().strip('\n')
    answer = answer.lower() if l else answer
    return answer

def yn(question):
    while True:
        answer = ask("{0} [yes/no]".format(question),True)
        d = difflib.SequenceMatcher(a='yes',b=answer)
        rat = d.ratio()*100
        if rat >= 50:
            return True
        else:
            d.set_seq1('no')
            rat = d.ratio()*100
            if rat >= 50:
                return False
            else:
                print("Sorry, That wasn't an option\n")
                continue

def main():
    while True:
        patha = ask("Which is your repo's path? (Need an absolute path)")
        if not os.path.exists(patha):
            print("Hmm, looks like that path doesn't exist, Are you sure that it's there?\n")
            continue
        if not os.path.exists(os.path.join(patha,'.git')):
            print("Looks like that the path you gave is not a git repo\n")
            continue
        while True:
            repo = ask("And what is your repo called? (Give the full name, eg: necessary129/GitFetcher)")
            if '/' in repo:
                break
            else:
                print("Are you sure that it's a full name? See the example above\n")
        add(repo,patha)
        if not yn("Do you want to add another repo?"):
            break
    print(after_making)

if __name__ == '__main__':
    main()
else:
    print("No!")