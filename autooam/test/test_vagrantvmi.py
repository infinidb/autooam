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
    return (myret, mydata, "")

class VagrantVMITest(unittest.TestCase):


    def setUp(self):
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


    def test_poweroffon(self):
        '''OBE.  leaving file here for future tests'''
        pass

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
