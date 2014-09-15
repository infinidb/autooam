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
autooam.vmi.vagstatus

Expose a method to retrive vagrant box status information
'''

import os
import re
from collections import defaultdict

def vagrant_status(vagrantdir,unittest=''):
    '''Returns a dictionary with status for a cluster.
    
    @param vagrantdir - directory to run the 'vagrant status' command in
    @param unittest - [optional] read input from a file instead of executing 'vagrant status'
    
    Returns a dictionary that always contains a 'cluster' entry plus
    one entry for each machine found in the cluster.
    
    Machine states are one of ('not created', 'poweroff', 'running', 'saved').
    See VMI.status() for documentation of cluster statuses
    '''
    patt = re.compile('^(\w+)\s+([a-z ]+)$')
    patt2 = re.compile('^(\w+)\s+([a-z ]+) \(.*\)$') # newer vagrant changes status output
    
    ret = {}
    if not unittest and not os.path.exists('%s/Vagrantfile' % vagrantdir):
        raise Exception("Directory %s does not appear to be a valid Vagrant environment!" % vagrantdir)

    if unittest:
        cursor = open(unittest)
    elif os.system('which vagrant > /dev/null') >> 8:
        # we have no vagrant executable - assume this is unit testing without explicit input
        return { 'cluster' : 'not created' }
    else:
        owd = os.getcwd()
        os.chdir(vagrantdir)
        cmd = 'vagrant status'
        cursor = os.popen(cmd)
        os.chdir(owd)

    counter=defaultdict(int)
    for line in cursor:
        m = patt.match(line)
        m2 = patt2.match(line)
        if m2 != None:
            ret[m2.group(1)] = m2.group(2)
            counter[m2.group(2)] += 1
        elif m != None:
            ret[m.group(1)] = m.group(2)
            counter[m.group(2)] += 1
    
    # now set the overall cluster status
    if len(ret) == 0:
        ret['cluster'] = 'unknown'
    elif counter['not created'] == len(ret):
        ret['cluster'] = 'not created'
    elif counter['not created'] > 0:
        ret['cluster'] = 'partially created'
    elif counter['poweroff'] == len(ret):
        ret['cluster'] = 'poweroff'
    elif counter['saved'] == len(ret):
        ret['cluster'] = 'saved'
    elif counter['poweroff'] > 0:
        ret['cluster'] = 'partially up'
    elif counter['running'] == len(ret):
        ret['cluster'] = 'running'
    else:
        ret['cluster'] = 'unknown'
    
    return ret
