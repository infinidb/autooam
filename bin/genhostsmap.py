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

#!/usr/bin/env python
'''
Simple utility to generate a file for inclusion in the /etc/hosts file on an autooam server
'''

if __name__ == '__main__':
    NUM_SUBNETS = 100
    NUM_HOSTS   = 10
    for i in range(1, NUM_SUBNETS+1):
        for j in range(1, NUM_HOSTS+1):
            print '192.168.%d.%d\t192-168-%d-%d' % (i, j, i, j)