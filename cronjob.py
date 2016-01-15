#!/usr/bin/python3


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


import subprocess
import os
import optparse
import sys

parser = optparse.OptionParser(usage='Usage: %prog [options]')
parser.add_option('', '--dir',
                      help='Determines what directory the application resides in and '
                      'should be started from.')

(options, args) = parser.parse_args()

if not options.dir:
    print("No dir given")
    sys.exit(1)

os.chdir(options.dir)

def restart():
    inst = subprocess.Popen("python3 main.py", close_fds=True,
                                stderr=subprocess.STDOUT,
                                stdin=None, stdout=subprocess.PIPE)
        inst.communicate()
        ret = inst.returncode
        sys.exit(ret)

def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def getpid(fi):
    with open(fi) as f:
        return int(f.read())

try:
    pid = getpid('GitFetcher.pid')
except FileNotFoundError:
    restart()

if not alive(pid):
    restart()
else:
    sys.exit(0)