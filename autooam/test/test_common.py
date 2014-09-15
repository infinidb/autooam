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
autooam.test.test_common

module set up to be included by every other unit test module and adjust default configurations, etc.
'''

import os
import emtools.common as common
import autooam.common.properties as properties
import emtools.common.utils as utils

def mysyscb(cmd):
    return (0,'na','')

# re-initialize properties without loading site config
common.props = properties.Properties(unittest=True)
common.props['emtools.unittest'] = True
common.props['vmi.vagrantvmi.unit-test'] = True
common.props['common.oammongo.dbname'] = 'unit-test'
common.props['vmi.versionmgr.basedir'] = '%s/pkg-test' % os.path.dirname(__file__)
common.props['vmi.versionmgr.packagedir'] = '%s/pkg-cache' % os.path.dirname(__file__)

# need to disable real system calls for unit-test
utils.syscall_cb = mysyscb
