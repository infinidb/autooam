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

#!/usr/bin/env python
'''
Command-line utility to check for orphaned vms that exist in virtualbox but not autooam
'''

import os,sys
import getopt
import re
from sets import Set
import emtools.common.utils as utils
from autooam.cluster.clustermgr import ClusterMgr

def usage():
    print '''usage: cleanorphans [-h]
    
    Options:
        -h        : show usage
        -u        : unit-test mode
'''
    sys.exit(1)
    
def get_vbox_vms():
    vms = []
    (ret,output,outerr) = utils.syscall_log('vboxmanage list vms')
    lines = output.split('\n')
    for l in lines:
        if len(l):
            mat = re.search('^\"(.*)\" \{(.*)\}$',l)
            if not mat:
                sys.stderr.write("Unable to parse vm spec %s " % l)
                sys.exit(1)
            vms.append((mat.group(1),mat.group(2)))
    return vms
    
def kill_autorun_procs():
    # return from ps |grep will look like this
    # infinidb  5882     1  0 08:05 ?        00:00:00 /bin/sh /home/infinidb/Calpont/mysql//bin/mysqld_safe --defaults-file=/home/infinidb/Calpont/mysql//my.cnf --datadir=/home/infinidb/Calpont/mysql/db --pid-file=/home/infinidb/Calpont/mysql/db/pm1.pid
    (ret,output,outerr) = utils.syscall_log('ps -ef | grep autorun | grep -v grep')
    if ret:
        # means grep failed so nothing to do
        return
    else:
        lines = output.split('\n')
        for l in lines:
            # split on whitespace
            fields = l.split()
            if len(fields) >= 2:
                print 'Found rogue process %s...Killing' % fields[8]
                pid = fields[1]
                cmd = 'kill -9 %s' % pid
                print "Issuing: %s" % cmd
                utils.syscall_log(cmd)
        
def mysyscb(cmd):
    if cmd == 'vboxmanage list vms':
        return (0,""""512bf395d174b03784c74c2b_1361834924" {e857f2f2-c08b-4e52-b3c1-562420d33ed8}
"512bf395d174b03784c74c2b_1361835016" {7b21bb6b-df28-42c6-a853-227a4dcd06c7}
"512bf395d174b03784c74c2b_1361835108" {493b6aec-2c3c-4f7d-88e4-95cca55dceff}
"51383ad6d174b017791ff467_1362639595" {f0c06bfc-7d0a-44a9-93d3-53cc783af045}
""","")
    elif cmd == 'ps -ef | grep autorun | grep -v grep':
        return (0,'infinidb  5882     1  0 08:05 ?        00:00:00 /bin/sh /home/infinidb/Calpont/mysql//bin/mysqld_safe --defaults-file=/home/infinidb/Calpont/mysql//my.cnf --datadir=/home/infinidb/Calpont/mysql/db --pid-file=/home/infinidb/Calpont/mysql/db/pm1.pid','')
    else: 
        return (0,'na','')
        
def main(argv=None):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "pu", [])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    killprocs = False
    for o, a in opts:
        if o == "-p":
            killprocs = True
        elif o == "-u":
            import autooam.test.test_common
            utils.syscall_cb = mysyscb
        else:
            assert False, "unhandled option"

    if killprocs:
        kill_autorun_procs()
        
    # first get the list of registered vms from virtualbox
    vms = get_vbox_vms()

    mgr = ClusterMgr()    
    ids = Set()
    for c in mgr.list_clusters():
        ids.add(c[1])
        
    for vm in vms:
        print "Checking vm %s" % vm[0],
        if vm[0] == "<inaccessible>":
            print "...Orphaned, Deleting"
            cmd = "vboxmanage unregistervm %s --delete" % vm[1]
            print "Issuing: %s" % cmd
            utils.syscall_log(cmd)
        else:
            _id = vm[0].split('_')[0]
            if not _id in ids:
                print "...Orphaned, Deleting"
                cmd = "vboxmanage unregistervm %s --delete" % vm[0]
                print "Issuing: %s" % cmd
                utils.syscall_log(cmd)
            else:
                print "...Ok"

if __name__ == "__main__":
    sys.exit(main())
