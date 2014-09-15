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
Created on Dec 20, 2012

@author: rtw
'''
import unittest
import emtools.common as common
import os

class PropertiesTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBasic(self):
        # don't need to test much - emtools tests all the functionality of properties
        # we just need to make sure our properties got loaded
        self.assertTrue( 'vmi.vagrantvmi.defmemsize' in common.props )
        self.assertTrue( common.props.has_key('vmi.vagrantvmi.defmemsize') )
        # and sanity to make sure we also have emtools
        self.assertTrue( 'emtools.logname' in common.props )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
