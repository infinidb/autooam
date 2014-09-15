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
Created on Sep 19, 2013

@author: rtw
'''
import unittest
from autooam.cluster.clustermgr import ClusterMgr
from emtools.cluster.configspec import ConfigSpec
from autooam.whirr.whirrconf import WhirrConfigWriter
from autooam.common.oammongo import AutoOamMongo
import testutils
import test_common
import json
import os

class WhirrConfTest(unittest.TestCase):


    def setUp(self):
        # clean out the test db
        dbcon = AutoOamMongo()
        dbcon.db().clusters.remove()
        dbcon.db().allocs.remove()

        self._basedir = os.path.dirname(os.path.abspath(__file__))
        self._propcmp = '%s/hadoop.properties' % self._basedir
        self._nodecmp = '%s/nodes-byon.yaml' % self._basedir

    def tearDown(self):
        pass

    def test1(self):
        #print '++++++++++ DEBUG: starting test1'
        s = """{
            "name" : "a-cluster",
            "idbversion" : "Latest", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 1
                }
              },
            "hadoop"     : {
              "instance-templates" : "1 hadoop-namenode+hadoop-jobtracker,2 hadoop-datanode+hadoop-tasktracker"
              }
            }
            """
        mgr = ClusterMgr()
        
        c = mgr.alloc_new('my-clustername',ConfigSpec(s),'vagrant')
        w = WhirrConfigWriter(c)
        w.write_config(self._basedir)
        ref_file = '%s/testwhirr-props' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, self._propcmp))
        ref_file = '%s/testwhirr-nodes' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, self._nodecmp))

        mgr.destroy(c)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
