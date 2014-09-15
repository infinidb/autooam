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
Created on Jan 9, 2013

@author: rtw
'''
import unittest
import os
import getpass
from autooam.testmgr.testmgr import TestManager
import emtools.common as common
import emtools.common.utils as utils
import autooam.testlib.tests as tests
import autooam.testlib.configs as configs
import test_common

def mysyscb(cmd):
    return (0,"","")

def mysyscb2(cmd):
    if cmd == 'vagrant --parallel up':
        return (-1,'oops',"")
    return (0,"","")

def mysyscb3(cmd):
    return (-1,'oops',"")

class TestManagerTest(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBasic(self):
        # turn on unit-test mode so that we don't actually run vagrant commands
        common.props['vmi.vagrantvmi.unit-test'] = True
        
        cfg1 = configs.multi_1um_2pm('3.5.1-5')
        cfg1['boxtype'] = 'cal-precise64'
        cfg2 = configs.multi_1um_2pm('3.5.1-5')
        cfg2['boxtype'] = 'cal-lucid64'
        runlist = [ (cfg1, 'vagrant', tests.basic001()),
                    (cfg2, 'vagrant', tests.basic001()) ]

        mgrfile = '/tmp/%s_test_testmgr.log' % getpass.getuser()
        mgr = TestManager(mgrfile)

        # need to disable real system calls for unit-test
        utils.syscall_cb = mysyscb

        self.assertTrue( mgr.run_all(runlist) )
        self.assertEqual(mgr.test_report().passing(), 6)
        self.assertEqual(mgr.test_report().failing(), 0)
        self.assertEqual(mgr.test_report().total(), 6)
        utils.syscall_cb = None

        os.remove(mgrfile)

    def testBasicEm(self):
        # turn on unit-test mode so that we don't actually run vagrant commands
        common.props['vmi.vagrantvmi.unit-test'] = True
        
        cfg1 = configs.multi_1um_2pm('4.5.0-1')
        cfg1['boxtype'] = 'cal-precise64'
        cfg1['binary'] = True
        cfg1['em'] = { 'present' : True, 'invm' : True, 'emhost' : 'localhost', 'emport' : 9090, 'boxtype' : 'cal-centos6', 'oamserver_role' : "pm1", "role" : "em1" }
        runlist = [ (cfg1, 'vagrant', tests.basic001()) ]

        mgrfile = '/tmp/%s_test_testmgr.log' % getpass.getuser()
        mgr = TestManager(mgrfile)

        # need to disable real system calls for unit-test
        utils.syscall_cb = mysyscb

        ret = mgr.run_all(runlist)
        self.assertTrue( ret )
        self.assertEqual(mgr.test_report().passing(), 10)
        self.assertEqual(mgr.test_report().failing(), 0)
        self.assertEqual(mgr.test_report().total(), 10)
        utils.syscall_cb = None

        os.remove(mgrfile)

    def testStartupFailure(self):
        # turn on unit-test mode so that we don't actually run vagrant commands
        common.props['vmi.vagrantvmi.unit-test'] = True
        
        cfg1 = configs.multi_1um_2pm('3.5.1-5')
        cfg1['boxtype'] = 'cal-precise64'
        cfg2 = configs.multi_1um_2pm('3.5.1-5')
        cfg2['boxtype'] = 'cal-lucid64'
        runlist = [ (cfg1, 'vagrant', tests.basic001()),
                    (cfg2, 'vagrant', tests.basic001()) ]

        mgrfile = '/tmp/%s_test_testmgr.log' % getpass.getuser()
        mgr = TestManager(mgrfile)

        # need to disable real system calls for unit-test
        utils.syscall_cb = mysyscb2

        self.assertFalse( mgr.run_all(runlist) )
        self.assertEqual(mgr.test_report().passing(), 0)
        self.assertEqual(mgr.test_report().failing(), 2)
        self.assertEqual(mgr.test_report().total(), 2)
        utils.syscall_cb = None

        os.remove(mgrfile)
    
    def testStartupAbort(self):
        # turn on unit-test mode so that we don't actually run vagrant commands
        common.props['vmi.vagrantvmi.unit-test'] = True
        
        cfg1 = configs.multi_1um_2pm('3.5.1-5')
        cfg1['boxtype'] = 'cal-precise64'
        cfg2 = configs.multi_1um_2pm('3.5.1-5')
        cfg2['boxtype'] = 'cal-lucid64'
        runlist = [ (cfg1, 'vagrant', tests.basic001()),
                    (cfg2, 'vagrant', tests.basic001()) ]

        mgrfile = '/tmp/%s_test_testmgr.log' % getpass.getuser()
        mgr = TestManager(mgrfile)

        # need to disable real system calls for unit-test
        utils.syscall_cb = mysyscb3

        self.assertFalse( mgr.run_all(runlist) )
        self.assertEqual(mgr.test_report().passing(), 0)
        self.assertEqual(mgr.test_report().failing(), 2)
        self.assertEqual(mgr.test_report().total(), 2)
        utils.syscall_cb = None

        os.remove(mgrfile)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
