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
Command-line utility to interact with clusters (see usage)
'''

import os,sys,getopt
import json
import re
from autooam.cluster.clustermgr import ClusterMgr
from autooam.common.oammongo import AutoOamMongo
from autooam.testsuite.testrunner import TestRunner
import autooam.testlib.tests as tests
import emtools.common.logutils as logutils

Log = logutils.getLogger(__name__)

class ClusterCmd(object):
    def __init__(self):
        self._mgr = ClusterMgr()
    
    def main(self,argv=None):
        if not argv:
            argv = sys.argv
            
        try:
            opts, args = getopt.getopt(argv[1:], "u", [])
        except getopt.GetoptError as err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognized"
            self.usage()
            sys.exit(2)
    
        for o, a in opts:
            if o == "-u":
                import autooam.test.test_common
                # reinitialize this to pickup debug db
                self._mgr = ClusterMgr()
            else:
                assert False, "unhandled option"

        cmdaction = {
            'list'    : self.listclusters,
            'start'   : self.start,
            'poweron' : self.poweron,
            'poweroff': self.poweroff,
            'pause'   : self.pause,
            'resume'  : self.resume,
            'destroy' : self.destroy,
            'shell'   : self.shell,
            'show'    : self.show,
            'forceclean' : self.forceclean,
            'run'     : self.run,
            'attach'  : self.attach
        }
    
        if len(args) < 1 or not cmdaction.has_key(args[0]):
            self.usage()
            
        return cmdaction[args[0]](args[1:])

    def usage(self):
        print '''usage: clustercmd [-u] command [command options] ...
        
            -u  : enable unit-test mode
            
        Supported command options:
            list
                : list all clusters
            start cluster
                : start the cluster with name <cluster>
            poweron cluster
                : powers on the cluster with name <cluster>
            poweroff cluster
                : powers off the cluster with name <cluster>
            pause cluster
                : pauses the cluster with name <cluster>
            resume cluster
                : resumes the cluster with name <cluster>
            destroy <regex>
                : destroy any clusters with name  or ID matching <regex>
            shell cluster node cmd
                : run 'cmd' on node 'node' in the named cluster
            show cluster
                : show details for the cluster with name <cluster>            
            forceclean cluster
                : destroy and clean cluster, even if in inconsistent state
            run cluster test
                : run the test suite named 'test' on <cluster>            
            attach cluster emhost emport
                : attempt an attach from EM server <emhost>:<emport> to <cluster>            
        '''
        sys.exit(1)
        
    def listclusters(self,args):
        print 'Clusters: (name, id)'
        for c in self._mgr.list_clusters():
            sync = 'ok'
            try:
                cluster = self._mgr.attach( c[0] )
                sync = 'ok,%s' % cluster.status()
            except Exception, err:
                sync = 'invalid (%s),n/a' % err
            print '\t(%s,%s,%s)' % (c[0], c[1], sync)
        return 0
        
    def _attach_by_name(self, name):
        try:
            cluster = self._mgr.attach( name )
        except Exception, err:
            Log.error("Unable to attach to cluster %s, %s" % (name, err))
            sys.exit(-1)
        return cluster            
        
    def start(self,args):
        if not len(args) == 1:
            self.usage()
            
        cluster = self._attach_by_name(args[0])
        return cluster.start()
    
    def poweron(self,args):
        if not len(args) == 1:
            self.usage()
            
        cluster = self._attach_by_name(args[0])
        return cluster.poweron()
    
    def poweroff(self,args):
        if not len(args) == 1:
            self.usage()
            
        cluster = self._attach_by_name(args[0])
        return cluster.poweroff()
    
    def pause(self,args):
        if not len(args) == 1:
            self.usage()
            
        cluster = self._attach_by_name(args[0])
        return cluster.pause()

    def resume(self,args):
        if not len(args) == 1:
            self.usage()
            
        cluster = self._attach_by_name(args[0])
        return cluster.resume()

    def destroy(self,args):
        if not len(args) == 1:
            self.usage()
            
        regex = re.compile('^%s$' % args[0])
        ret = 0
        foundone = False
        for c in self._mgr.list_clusters():
            if regex.match(c[0]):
                foundone = True
                cluster = self._attach_by_name(c[0])
                Log.info('Destroying cluster %s...' % c[0])
                if not self._mgr.destroy(cluster):
                    ret = 1
                    
        if not foundone:
            try:
                if not self._mgr.destroy_by_id(args[0]):
                    ret = 1
                else:
                    foundone = True
            except:
                ret = 1
                
        if not foundone:
            Log.warning('No clusters matched pattern \'%s\'' % args[0])
            
        return ret
    
    def forceclean(self,args):
        if not len(args) == 1:
            self.usage()

        dbcon = AutoOamMongo()
        cdefn = dbcon.db().clusters.find_one( { 'name' : args[0] } )
        if not cdefn:
            Log.error("Cluster %s not found!" % args[0])
            return -1

        # clean the two databases
        dbcon.db().allocs.remove( { 'cid' : cdefn['_id'] } )
        dbcon.db().clusters.remove( { '_id' : cdefn['_id'] } )
        
        # now wipe any remnants in the file system
        cmd = 'rm -rf %s' % cdefn['vmi']['rundir']
        os.system(cmd)            

    def shell(self,args):
        if not len(args) == 3:
            self.usage()

        name = args[0]
        node = args[1]
        cmd  = args[2]

        cluster = self._attach_by_name(name)
        return cluster.shell_command(node, cmd)
    
    def show(self,args):
        if not len(args) == 1:
            self.usage()
            
        cluster = self._attach_by_name(args[0])
        print 'Cluster %s' % cluster.name()
        print 'id        : %s' % cluster.id()
        print 'config    : ',
        print json.dumps(cluster.config().json_dumps(), sort_keys=True, indent=4, separators=(',', ': ')) 
        print 'vmi       : ',
        print json.dumps(cluster.get_vmi().jsonmap(), sort_keys=True, indent=4, separators=(',', ': ')) 
        print 'machines  : ',
        print json.dumps(cluster.machines(), sort_keys=True, indent=4, separators=(',', ': ')) 
        print 'status  : %s' % cluster.status()

    def run(self,args):
        if not len(args) == 2:
            self.usage()
            
        cluster = self._attach_by_name(args[0])
        tr = TestRunner()
        testsuite = tests.call_by_name(args[1])
        result = tr.run(cluster, testsuite)
        print 'Status:', 'Pass' if result.passfail() else 'Fail'

    def attach(self,args):
        if not len(args) == 3:
            self.usage()

        name = args[0]
        emhost = args[1]
        emport = int(args[2])

        cluster = self._attach_by_name(name)
        return cluster._em_attach(emhost=emhost, emport=emport)
            
if __name__ == "__main__":
    cmd = ClusterCmd()
    sys.exit(cmd.main())
