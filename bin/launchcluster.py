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

import sys,getopt
from autooam.cluster.clustermgr import ClusterMgr
from emtools.cluster.configspec import ConfigSpec
import autooam.testlib.configs as configs
import emtools.common.logutils as logutils

Log = logutils.getLogger(__name__)

def usage():
    print '''usage: usage: launchcluster.py [-hlfun] name config boxtype version
    
    Options:
        -h  : show usage
        -l  : list all supported configs
        -f  : load ConfigSpec from file <config>
        -u  : enable unit-test mode
        -n  : bring up cluster but do not install InfiniDB
        
    name    : cluster name
    config  : configuration to use
    boxtype : vagrant box type
    version : InfiniDB version 
'''
    
def main(argv=None):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "lfun", [])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    cfile = False
    install = True
    for o, a in opts:
        if o == "-l":
            for c in configs.list_all():
                print '%-20s : %s' % (c[0], c[1])
            return 0
        elif o == "-f":
            cfile = True
        elif o == "-u":
            import autooam.test.test_common
        elif o == "-n":
            install = False
        else:
            assert False, "unhandled option"
                
    if len(args) != 4:
        usage()
        sys.exit(2)
        
    Log.info("Creating new cluster instance %s" % args[0])
    
    name   = args[0]
    config = args[1]
    box    = args[2]
    version = args[3]

    mgr = ClusterMgr()
    if cfile:
        cfg = ConfigSpec(jsonfile=config,idbversion=version,boxtype=box)
    else:
        cfg = configs.call_by_name(config, version, boxtype=box)
    #dmc control chef vs ansible mode through chefmode flag
    c = mgr.alloc_new(name,cfg,'vagrant', chefmode=False)
    ret = c.start()
    if ret != 0:
        Log.error("Cluster start failed...aborting launch")
        return ret
    if install:
        c.run_install_recipe()

if __name__ == "__main__":
    sys.exit(main())
