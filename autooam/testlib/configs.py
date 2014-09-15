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
autooam.testlib.configs

Functors for config specs.

All config spec functors require exactly 1 argument:
idbversion - InfiniDB version to use
'''

import sys,inspect
import vagboxes
from emtools.cluster.configspec import ConfigSpec

def singlenode(idbversion):
    '''single node system - 1 combined UM/PM.'''
    s = '''
    {
        "name" : "single",
        "rolespec" : {
            "pm" : {
                "count" : 1,
                "dbroots_per" : 1
                }
            }
    }
    '''
    return ConfigSpec(jsonstring=s, idbversion=idbversion)

def multi_2umpm_combo(idbversion):
    '''two node combination system - 2 combined UM/PMs.'''
    s = '''
    {
        "name" : "2umpm_combo",
        "rolespec" : {
            "pm" : {
                "count" : 2,
                "dbroots_per" : 1
                }
            }
    }
    '''
    return ConfigSpec(jsonstring=s, idbversion=idbversion)

def multi_1um_2pm(idbversion):
    '''3 node cluster with 1 UM, 2 PMs and 1 dbroot per PM.'''
    s = '''
    {
        "name" : "1um_2pm",
        "rolespec" : {
            "pm" : {
                "count" : 2,
                "dbroots_per" : 1
                },
            "um" : {
                "count" : 1
                }
            }
    }
    '''
    return ConfigSpec(jsonstring=s, idbversion=idbversion)

# this code automatically registers ever config function in the
# register array by (name, doc-string)

def list_all():
    register = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj) and name != 'list_all' and name != 'call_by_name':
            register.append((obj.func_name,obj.__doc__, obj))
    return register

def call_by_name(name, idbversion, boxtype=None):
    thismodule = sys.modules[__name__]
    fn = getattr(thismodule,name)
    cfg = fn(idbversion)
    if boxtype:
        vagboxes.validate(boxtype)
        cfg['boxtype'] = boxtype
    return cfg
