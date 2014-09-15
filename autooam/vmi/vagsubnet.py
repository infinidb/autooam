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
autooam.vmi.vagsubnet

Class to manage the allocation of subnets on creation of vagrant clusters
'''

from pymongo import MongoClient
from autooam.common.oammongo import AutoOamMongo

class VagrantSubnetAlloc(object):
    '''
    The creation of Vagrant clusters requires the allocation of an IP subnet
    for VirtualBox host-only networking.  There are any number of ways this 
    could be accomplished, but for now VagrantSubnetAlloc scans the cluster
    database and looks for the first unused subnet.  It starts scanning at
    192.168.1.x and will look until it finds one.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._dbcon = AutoOamMongo()
        self._db = self._dbcon.db().clusters

    def alloc(self, cluster):
        # when allocating new we need to first find an unused subnet
        start = 0xc0a801 # 192.168.1
        subnet = '%d.%d.%d' % ((start >> 16) & 0xff,(start >> 8) & 0xff,start & 0xff)
        while self._db.find( { 'vmi.subnet' : subnet }).count():
            start += 1
            subnet = '%d.%d.%d' % ((start >> 16) & 0xff,(start >> 8) & 0xff,start & 0xff)

        return subnet
