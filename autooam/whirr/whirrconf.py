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
autooam.whirr.whirrconf

Utility class that writes out config files for whirr
'''

import autooam.testlib.vagboxes as vagboxes
import emtools.common as common

class WhirrConfigWriter(object):
    '''
    WhirrConfigWriter encapsulates the logic to be able to write out the
    required Whirr configuration for a particular cluster specification.
    This will include:
        hadoop.properties - Whirr properties file
        nodes-byon.yaml   - node definition for BYON config
    '''

    def __init__(self, cluster):
        '''
        Constructor
        '''
        self._cluster = cluster
        
    def write_config(self, dir_ = '.', prop = 'hadoop.properties', nodes = 'nodes-byon.yaml'):
        '''
        Writes the two configuration files to the specified directory
        '''
        pf = open( '%s/%s' % (dir_, prop), 'w')
        pf.write('whirr.cluster-name=%s\n' % self._cluster.name())
        pf.write('whirr.cluster-user=vagrant\n')
        pf.write('whirr.instance-templates=%s\n' % self._cluster.config()['hadoop']['instance-templates'])
        if self._cluster.config()['hadoop'].has_key('templates-namenode'):
            pf.write('whirr.templates.hadoop-namenode+hadoop-jobtracker.byon-instance-ids=%s\n' %
                self._cluster.config()['hadoop']['templates-namenode'])
        if self._cluster.config()['hadoop'].has_key('templates-datanode'):
            pf.write('whirr.templates.hadoop-datanode+hadoop-tasktracker.byon-instance-ids=%s\n' %
                self._cluster.config()['hadoop']['templates-datanode'])
        pf.write('whirr.service-name=byon\n')
        pf.write('whirr.provider=byon\n')
        pf.write('jclouds.byon.endpoint=file://%s/%s\n' % (dir_, nodes))
        pf.write('whirr.provider=whirr.java.install-function = install_oracle_jdk6\n')
        if self._cluster.config()['hadoop'].has_key('version'):
            pf.write('whirr.hadoop.version=%s\n' % self._cluster.config()['hadoop']['version'])
            pf.write('whirr.hadoop.tarball.url=http://archive.apache.org/dist/hadoop/core/hadoop-${whirr.hadoop.version}/hadoop-${whirr.hadoop.version}.tar.gz\n')
        else:
            pf.write('whirr.hadoop.install-function=install_cdh_hadoop\n')
            pf.write('whirr.hadoop.configure-function=configure_cdh_hadoop\n')
        pf.close()
        
        nf = open( '%s/%s' % (dir_, nodes), 'w' )
        nf.write('nodes:\n')
        for m in sorted(self._cluster.machines()):
            if not m == 'em1': # exclude dedicated EM server
                mach = self._cluster.machine(m)
                nf.write('    - id: %s\n' % m)
                nf.write('      hostname: %s\n' % mach['ip'])
                nf.write('      os_arch: x86_64\n')
                boxtype = self._cluster.config()['boxtype']
                nf.write('      os_family: %s\n' % vagboxes.get_os_family(boxtype))
                nf.write('      os_description: %s\n' % vagboxes.get_description(boxtype))
                nf.write('      os_version: %s\n' % vagboxes.get_os_version(boxtype))
                nf.write('      group: vagrant\n')
                nf.write('      username: vagrant\n')
                nf.write('      credential_url: file://%s/insecure_private_key\n' % common.props['vmi.vagrantvmi.vagrantroot'])
                nf.write('      sudo_password:\n')
        nf.close()
        
