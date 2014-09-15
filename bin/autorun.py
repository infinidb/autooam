# Copyright (C) 2014 InfiniDB, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2 of
# the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA. 

#!/usr/bin/python
'''
Command-line utility to kick off a test run
'''

import sys
import getopt
import autooam.testlib.runlists as runlists
from autooam.testmgr.testmgr import TestManager
import random

def usage():
    print '''usage: autorun [-lr:] version run-list log-file
    
    Options:
        -h        : show usage
        -l        : list all supported run lists
        -r <num>  : run <num> randomly selected entries from the runlist 
        -s        : run with standard (i.e. non-enterprise packages)
        
    version : InfiniDB version to run
    run-list: name of the run-list functor
    log-file: name of the log file to write 
'''
    sys.exit(1)
    
def main(argv=None):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "lr:s", [])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    numrand = 0
    enterprise = True
    for o, a in opts:
        if o == "-l":
            for r in runlists.list_all():
                print '%-20s : %s' % (r[0], r[1])
            return 0
        elif o == "-r":
            numrand = int(a)
        elif o == "-s":
            enterprise = False
        else:
            assert False, "unhandled option"

    if len(args) < 3:
        usage()
        
    version = args[0]
    functor = args[1]
    logfile = args[2]
    
    if not runlists.__dict__.has_key(functor):
        print "No functor name %s in runlist" % functor
        
    mgr = TestManager(logfile)
    final_list = runlists.call_by_name(functor, version, 'vagrant', num=numrand, enterprise=enterprise)
    return mgr.run_all(final_list)    

if __name__ == "__main__":
    sys.exit(main())
