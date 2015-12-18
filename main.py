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

from imp import reload
import gitfetcher
import os
import os.path
from time import sleep
from threading import Thread
import sys

fl = os.path.abspath('GitFetcher.py')
last_change = os.stat(fl).st_mtime
aa = False

def check_change():
    while True:
        global last_change
        global aa
        lchange = os.stat(fl).st_mtime
        if lchange != last_change:
            last_change = lchange
            if gitfetcher.httpd:
                gitfetcher.httpd.shutdown()
            print("File has changed, restarting.......")
            reload(gitfetcher)
            aa = True
        else:
            sleep(1)

chra = Thread(target=check_change,daemon=True)
chra.start()
try:
    gitfetcher.main()
except (KeyboardInterrupt, EOFError):
    sys.exit(0)

while True:
    if aa:
        aa = False
        try:
            gitfetcher.main()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
