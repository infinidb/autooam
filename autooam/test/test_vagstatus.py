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
Created on Jan 4, 2013

@author: rtw
'''
import unittest
import autooam.vmi.vagstatus as vagstatus
import os

class VagstatusTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testStatus(self):
        testfile = '%s/test1-vagstatus' % os.path.dirname(__file__)
        ret = vagstatus.vagrant_status('.', testfile)
        self.assertEqual( ret['cluster'], 'not created')
        self.assertEqual( ret['pm1'], 'not created')
        self.assertEqual( ret['pm2'], 'not created')
        self.assertEqual( ret['um1'], 'not created')

    def test2Status(self):
        testfile = '%s/test2-vagstatus' % os.path.dirname(__file__)
        ret = vagstatus.vagrant_status('.', testfile)
        self.assertEqual( ret['cluster'], 'running')
        self.assertEqual( ret['pm1'], 'running')
        self.assertEqual( ret['pm2'], 'running')
        self.assertEqual( ret['um1'], 'running')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testStatus']
    unittest.main()