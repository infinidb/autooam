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

'''
Created on Dec 18, 2012

@author: rtw
'''
import unittest
import emtools.common.utils as utils
from emtools.cluster.configspec import ConfigSpec
from autooam.cluster.clustermgr import ClusterMgr
from autooam.common.oammongo import AutoOamMongo
from autooam.testsuite.testrunner import TestRunner
import emtools.common as common
import autooam.testlib.tests as tests
import test_common
import re

# simple callback setup to test the debug version of syscall
myret = 0
mydata = ''
mycmds = []
def mysyscb(cmd):
    global mycmd
    mycmds.append( cmd )
    return (myret, mydata, '')

def mysyscb2(cmd):
    global mycmd
    mycmds.append( cmd )
    if cmd[0:3] == 'ssh':
        return (1,'Failed','')
    else:
        return (0,'','')

class TestsTest(unittest.TestCase):


    def setUp(self):
        # turn on unit-test mode so that we don't actually run vagrant commands
        common.props['vmi.vagrantvmi.unit-test'] = True

        # clean out the test db
        dbcon = AutoOamMongo()
        dbcon.db().clusters.remove()
        dbcon.db().allocs.remove()

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-5", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "memory" : 1024,
                    "dbroots_per" : 1
                }
              }
            }
            """
        self._defcfg = ConfigSpec(s)

    def tearDown(self):
        pass

    def check_syscalls(self, callpats):
        global mycmds

        if len(mycmds) != len(callpats):
            for i in range(0,len(mycmds)):
                print "CMD #%d: %s" % (i, mycmds[i])
        self.assertEqual(len(mycmds), len(callpats))
        for i in range(0, len(callpats)):
            r = re.compile(callpats[i])
            self.assertIsNotNone(r.match(mycmds[i]), '%s : %s' % (mycmds[i], callpats[i]))

    def test_listall(self):
        list_ = tests.list_all()
        nameonly = []
        for l in list_:
            nameonly.append(l[0])
        self.assertEqual( nameonly, ['basic001', 'basic002', 'moduleFailover', 'upgrade001'])

    def test_basic001(self):
        # reset list of syscalls
        #print '++++++++++ DEBUG: starting test_basic001'
        global mycmds
        mycmds = []
        
        mgr = ClusterMgr()
        c1 = mgr.alloc_new('testsub1',self._defcfg,'vagrant')
        
        utils.syscall_cb = mysyscb
        
        c1.start()
        tr = TestRunner()
        testsuite = tests.call_by_name('basic001')
        result = tr.run(c1, testsuite)
        print 'Status:', 'Pass' if result.passfail() else 'Fail'
        
        # now check that the right system calls were executed
        callpats = [
            'vagrant.*up',
            'ssh.*echo',
            'ssh.*dbFunctional.sh'
            ]
        self.check_syscalls(callpats)
        utils.syscall_cb = None
                
        mgr.destroy(c1)

    def test_basic002(self):
        # reset list of syscalls
        #print '++++++++++ DEBUG: starting test_basic002'
        global mycmds
        mycmds = []
        
        mgr = ClusterMgr()
        c1 = mgr.alloc_new('testbasic002',self._defcfg,'vagrant')
        
        utils.syscall_cb = mysyscb
        
        c1.start()
        tr = TestRunner()
        testsuite = tests.call_by_name('basic002')
        result = tr.run(c1, testsuite)
        print 'Status:', 'Pass' if result.passfail() else 'Fail'
        
        # now check that the right system calls were executed
        callpats = [
            'vagrant.*up',
            'ssh.*echo',
            'ssh.*upgradeTest2.sh',
            'ssh.*calpontConsole shutdown y',
            'ssh.*sleep 5',
            'ssh.*infinidb_not_running.sh',
            'ssh.*calpontConsole startsystem',
            'ssh.*sleep 5',
            'ssh.*upgradeTest2.sh',
            'ssh.*calpontConsole restartsystem y',
            'ssh.*sleep 5',
            'ssh.*upgradeTest2.sh',
            'ssh.*calpontConsole stopsystem y',
            'ssh.*sleep 5',
            'ssh.*calpontConsole startsystem',
            'ssh.*sleep 5',
            'ssh.*upgradeTest2.sh',
            'ssh.*calpontConsole shutdown y',
            'ssh.*sleep 5',
            'ssh.*infinidb_not_running.sh',
            'vagrant halt',
            'vboxmanage startvm.*headless',
            'vboxmanage startvm.*headless',
            'ssh.*healthcheck',
            'ssh.*upgradeTest2.sh',
            ]
        self.check_syscalls(callpats)
        utils.syscall_cb = None
                
        mgr.destroy(c1)            
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
