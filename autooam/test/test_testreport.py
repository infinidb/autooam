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
from autooam.testmgr.testreport import TestReport
from autooam.cluster.clustermgr import ClusterMgr
from autooam.common.oammongo import AutoOamMongo
from autooam.testsuite.testsuite import TestSuite
from autooam.testsuite.testresult import TestResult
from datetime import datetime
import testutils
import autooam.testlib.configs as configs
import test_common

class TestReportTest(unittest.TestCase):

    def setUp(self):
        # use an alternate database for unit-testing
        dbcon = AutoOamMongo()
        dbcon.db().clusters.remove()
        dbcon.db().allocs.remove()


    def tearDown(self):
        pass


    def testBasic(self):
        #print '++++++++++ DEBUG: starting testBasic'
        if True:
            # put in a code block so that TestReport closed before we validate
            tr = TestReport('/tmp/trtest.log')
    
            mgr = ClusterMgr()
            
            cfg1 = configs.multi_1um_2pm('3.5.1-5')
            cfg1['boxtype'] = 'cal-precise64'
    
            c = mgr.alloc_new('test-report',cfg1,'vagrant')
    
            tr.new_config(c)
                            
            ts = TestSuite('my001','a unit test test suite')
            t = datetime.now()
            res = TestResult( t, t, True)
            tr.new_result(ts, res)
    
            ts = TestSuite('my002','another test suite')
            res = TestResult( t, t, False)
            tr.new_result(ts, res)
            
            mgr.destroy(c)
            # have to explicitly call this to make sure the file is closed
            tr.finish()

        ref_file = '%s/test1-testlog' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, '/tmp/trtest.log'))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
