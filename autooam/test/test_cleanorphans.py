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
Created on Mar 7, 2013

@author: rtw
'''
import os
import unittest
import emtools.common.utils as utils


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBasic(self):
        (ret, output, outerr) = utils.syscall_log('%s/bin/cleanorphans.py -u' % (os.environ['AUTOOAM_HOME']))
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/cleanorphans.py -u -p' % (os.environ['AUTOOAM_HOME']))
        self.assertEqual(ret,0,output)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
