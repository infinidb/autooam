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
Created on Jan 3, 2013

@author: rtw
'''
import unittest
import emtools.common as common
from autooam.vmi.vagsubnet import VagrantSubnetAlloc

class ClusterStub:
    def __init__(self, id):
        self._id = id
        
    def id(self):
        return self._id
    
class VagrantSubnetTest(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test1(self):
        # use an alternate database for unit-testing
        common.props['common.oammongo.dbname'] = 'unit-test'
        salloc = VagrantSubnetAlloc()
        salloc._db.remove()
        
        c1 = ClusterStub(1)
        subnet = salloc.alloc(c1)
        self.assertEquals( subnet, '192.168.1' )

        # we have to trick the allocator into thinking that 192.168.1 is used
        salloc._db.insert({ 'vmi' : { 'subnet' : subnet } })
        
        c2 = ClusterStub(2)
        subnet = salloc.alloc(c2)
        self.assertEquals( subnet, '192.168.2' )
                
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
