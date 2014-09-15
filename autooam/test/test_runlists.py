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
Created on Feb 20, 2013

@author: rtw
'''
import unittest
import autooam.testlib.runlists as runlists
import random
import test_common

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBasic(self):
        random.seed(1)

        rl = runlists.run_random_basic002('3.5.1-5', 'vagrant', num=1)
        self.assertEqual(len(rl), 1)

        rl = runlists.run_random_basic002('3.5.1-5', 'vagrant', num=2)
        self.assertEqual(len(rl), 2)

    def testSubset(self):
        random.seed(1)
        r = runlists.call_by_name('run001', '3.5.1-5', 'vagrant', 4)
        self.assertEqual(len(r),4)
        self.assertEqual(r[0][0]['boxtype'], 'cal-centos58')
        self.assertEqual(r[0][2].id(), 'basic001')
        self.assertEqual(r[1][0]['boxtype'], 'cal-precise64')
        self.assertEqual(r[2][0]['boxtype'], 'cal-precise64')
        self.assertEqual(r[3][0]['boxtype'], 'cal-centos6')
        
    def testSmoke(self):
        r = runlists.call_by_name('run_chef_smoketest', '3.5.1-5', 'vagrant')
        self.assertEqual(len(r),7)

    def testUpgrade(self):
        r = runlists.call_by_name('run_upgrade_suite', '3.5.1-5', 'vagrant')
        self.assertEqual(len(r),7)

    def testHadoop(self):
        r = runlists.call_by_name('run_hadoop_basic', 'Latest', 'vagrant')
        self.assertEqual(len(r),8)

    def testRunRandom(self):
        random.seed(1)
        r = runlists.call_by_name('run_random_basic002', '4.5.1-3', 'vagrant', 4)
        self.assertEqual(len(r),4)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
