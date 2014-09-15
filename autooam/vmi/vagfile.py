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
autooam.vmi.vagfile

Utility class that writes out a Vagrantfile
'''

import emtools.common as common
import os

class VagrantFileWriter(object):
    '''
    VagrantFileWriter encapsulates the logic to be able to write a Vagrantfile
    for a particular cluster specification
    '''

    def __init__(self,cluster, pkgfile, pkgversion, datdupfile, upgfile, upgvers, subnet, rundir):
        '''
        Constructor
        '''
        self._cluster = cluster
        self._pkgfile = pkgfile
        self._pkgversion = pkgversion
        self._datdupfile = datdupfile
        self._upgfile = upgfile
        self._upgvers = upgvers
        self._subnet = subnet
        self._rundir = os.path.basename(rundir)

    def writeVagrantFile(self, vfile):
        '''Writes a Vagrantfile to the specified location.'''
        vf = open( vfile, 'w' )
        vf.write('Vagrant::Config.run do |config|\n')
        self._writeHostFile(vf)
        # pm1 must go last because that is where we initiate the idb software install
        roles = self._cluster.machines().keys()
        for m in sorted(roles):
            if m != 'pm1':
                self._writeVMConfig(vf, m, self._cluster.machine(m))
        self._writeVMConfig(vf, "pm1", self._cluster.machine('pm1'))        
        vf.write('end\n')
        vf.close()
                
    def _writeHostFile(self,vf):
        cfg = self._cluster.config()
        vf.write('  host_map = {\n')
        vf.write('    :hostip => \'%s.1\',\n' % self._subnet)
        vf.write('    :autooam_home => \'%s\',\n' % os.environ['AUTOOAM_HOME'])
        vf.write('    :pkgfile => \'%s\',\n' % self._pkgfile)
        vf.write('    :pkgversion => \'%s\',\n' % self._pkgversion)
        if self._datdupfile:
            vf.write('    :datdupfile => \'%s\',\n' % self._datdupfile)      
        if self._upgfile:
            vf.write('    :upgfile => \'%s\',\n' % self._upgfile)
            vf.write('    :upgversion => \'%s\',\n' % self._upgvers)                  
        if cfg['hadoop']:
            # TODO-right now this is hardcoded for the CDH 2.0 Hadoop version
            # when HDP 1.3 support is added this will need to be conditional
            # based on ConfigSpec
            if cfg['hadoop'].has_key('version'):
                if cfg['hadoop']['version'][0:3] == '1.2':
                    vf.write('    :hadoopenv => \'%s\',\n' % '/root/setenv-hdfs-12')
                else:
                    vf.write('    :hadoopenv => \'%s\',\n' % '/root/setenv-hdfs-20')
            else:
                vf.write('    :hadoopenv => \'%s\',\n' % '/root/setenv-hdfs-20')
        vf.write('    :idbuser => \'%s\',\n' % cfg['idbuser'])            
        vf.write('    :dbroot_storage_type => \'%s\',\n' % cfg['storage'])
        vf.write('    :dbroot_count => \'%d\',\n' % cfg.total_dbroot_count())
        if cfg['storage'] == 'external':
            vf.write('    :remote_dbroot_basedir => \'%s\',\n' % self._rundir)
        else:
            vf.write('    :remote_dbroot_basedir => \'none\',\n')
        if self._cluster.config()['pm_query']:
                vf.write('    :postconfig_opts => \'%s\',\n' % ' -lq ')
        else:
                vf.write('    :postconfig_opts => \'%s\',\n' % ' ')
        vf.write('    :machines => [\n')
        first = True
        for m in sorted(self._cluster.machines()):
            mach = self._cluster.machine(m)
            if not first:
                vf.write(',\n')
            vf.write('      { :hostname => \'%s\', :role => \'%s\', :ip => \'%s\' }' % (mach['hostname'], m, mach['ip']))
            first = False
        vf.write('\n    ]\n  }\n')
             
    def _writeVMConfig(self,vf,role,rolemap):
        cfg = self._cluster.config()
        vf.write('\n')
        vf.write('config.vm.define :%s do |%s_config|\n' % (role,role))
        vf.write('  %s_config.vm.share_folder "pkgs", "/packages", "%s"\n' % (role, common.props['vmi.versionmgr.packagedir']))        
        vf.write('  %s_config.vm.host_name = "%s"\n' % (role,rolemap['hostname']))
        boxtype = cfg['boxtype'] if role != 'em1' else cfg['em']['boxtype']
        vf.write('  %s_config.vm.box = "%s"\n' % (role, boxtype))
        vf.write('  %s_config.vm.network :hostonly, "%s"\n' % (role, rolemap['ip']))
        if cfg['em']:
            real_oam_role = self._cluster.role_alias(cfg['em']['oamserver_role'])
            real_em_role = 'em1'
            # may not have an EM role if we are using a static EM
            if cfg['em'].has_key('role'):
                real_em_role = self._cluster.role_alias(cfg['em']['role'])
            subnet_part = self._subnet.split('.')[2]
            if role == real_oam_role:
                vf.write('  %s_config.vm.forward_port 8180,%d\n' % ( role, 9900 + int( subnet_part ) ))
            if role == real_em_role:
                vf.write('  %s_config.vm.forward_port 9090,%d\n' % ( role, 9000 + int( subnet_part ) ))                
        vf.write('  %s_config.vm.customize ["modifyvm", :id, "--memory", %d]\n' % (role,rolemap['memory']))
        vf.write('  %s_config.vm.customize ["modifyvm", :id, "--cpus", %d]\n' % (role,rolemap['cpus']))
        
        vf.write('  %s_config.vm.provision :chef_solo do |chef|\n' % role)
        vf.write('    chef.cookbooks_path = "%s/chef-repo/cookbooks"\n' % (os.environ['AUTOOAM_HOME']))
        vf.write('    chef.roles_path = "%s/chef-repo/roles"\n' % (os.environ['AUTOOAM_HOME']))
        vf.write('    chef.json = host_map\n')
        if cfg['idbuser'] == 'root':
            vf.write('    chef.add_role("root_key")\n')
        else:
            vf.write('    chef.add_role("nonrootuser")\n')
            
        if role[0:2] != 'em':
            # don't need to do any of these install steps if the node is for the EM
            if cfg['datdup']:
                vf.write('    chef.add_recipe("autooam::datdup_install")\n')       
    
            if cfg['hadoop']:
                vf.write('    chef.add_recipe("autooam::hadoop_preinstall")\n')       
    
            if cfg['binary']:
                if self._cluster.chefmode():
                    vf.write('    chef.add_recipe("autooam::binary_preinstall")\n')
            
        vf.write('  end\n')
        vf.write('end\n')
