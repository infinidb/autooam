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
import autooam.testlib.vagboxes as vagboxes

class TestLibTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBoxes(self):
        self.assertEqual( vagboxes.get_default_pkgtype('cal-precise64'), 'deb')
        self.assertEqual( vagboxes.get_os_family('cal-precise64'), 'ubuntu')
        self.assertEqual( vagboxes.get_os_version('cal-precise64'), '12.04')
        self.assertEqual( vagboxes.get_description('cal-precise64'), 'Ubuntu 12.04.1 LTS (Precise Pangolin)')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()