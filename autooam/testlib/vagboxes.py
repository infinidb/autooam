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
autooam.testlib.vagboxes

register and track vagrant box types supported by autooam
'''

'''
This may describes the known/supported box types.  Each box has the 
following fields:
    [0] - description of box type
    [1] - package type (deb or rpm)
    [2] - OS family (centos, ubuntu, debian)
    [3] - version 
    [4] - flags to indicate support for hadoop, EM, and datdup (gluster)
'''

FLAG_HADOOP = 0x01
FLAG_EM     = 0x02
FLAG_DATDUP = 0x04

register = {
    # legacy boxtypes - basic infinidb support only
    'cal-lucid64' : ('Ubuntu 10.04.4 LTS (Lucid Lynx)','deb', 'ubuntu', '10.04', 0),
    'cal-centos58' : ('CentOS release 5.8 (Final)','rpm', 'centos', '5.8', 0),
    
    # current boxtypes - full datdup, EM, hadoop support, etc. 
    'cal-precise64' : ('Ubuntu 12.04.1 LTS (Precise Pangolin)','deb', 'ubuntu', '12.04', FLAG_HADOOP | FLAG_EM | FLAG_DATDUP),
    'cal-trusty64' : ('Ubuntu 14.04 LTS (Trusty Tahr)','deb', 'ubuntu', '14.04', FLAG_HADOOP | FLAG_EM | FLAG_DATDUP),

    'cal-centos6' : ('CentOS release 6.5 (Final)','rpm', 'centos', '6.5', FLAG_HADOOP | FLAG_EM | FLAG_DATDUP), 

    'cal-debian6' : ('Debian 6.0.9 (Squeeze)','deb', 'debian', '6.0.9', FLAG_EM | FLAG_DATDUP), 
    'cal-debian7' : ('Debian 7.4 (Wheezy)','deb', 'debian', '7.4', FLAG_HADOOP | FLAG_EM | FLAG_DATDUP)
}

def get_default_pkgtype(boxtype):
    validate(boxtype)
    return register[boxtype][1]
    
def get_description(boxtype):
    validate(boxtype)
    return register[boxtype][0]
    
def get_os_family(boxtype):
    validate(boxtype)
    return register[boxtype][2]
    
def get_os_version(boxtype):
    validate(boxtype)
    return register[boxtype][3]

def get_flags(boxtype):
    validate(boxtype)
    return register[boxtype][4]
    
def hadoop_support(boxtype):
    '''
    Check whether or not the box supports Hadoop configuration.
    '''
    return ( get_flags( boxtype ) & FLAG_HADOOP ) != 0

def em_support(boxtype):
    '''
    Check whether or not the box supports EM configuration.
    '''
    return ( get_flags( boxtype ) & FLAG_EM ) != 0

def datdup_support(boxtype):
    '''
    Check whether or not the box supports datdup configuration.
    '''
    return ( get_flags( boxtype ) & FLAG_DATDUP ) != 0
    
def list_all( flags=0 ):
    '''
    Return a list of boxes.
    
    :param flags: flags mask to apply to boxes.  For example, to get all
                  boxes with Hadoop support do list_all( flags=FLAG_HADOOP )
    :returns: list of tuple (<box name>, <box description>)
    '''
    ret = []
    for k in register:
        if not( flags != 0 and ( ( get_flags(k) & flags ) == 0 ) ):
            ret.append( k )
    return sorted(ret)

def validate(box):
    if not register.has_key(box):
        raise Exception("Unknown box type: %s" % box)
