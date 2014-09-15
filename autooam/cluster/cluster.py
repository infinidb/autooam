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
autooam.cluster.cluster

Represent a group of machine instances that form a cluster
'''
import os
from emtools.cluster.playbookinstall import PlaybookInstall
import emtools.common.logutils as logutils
import emtools.common as common
import autooam.testlib.vagboxes as vagboxes
from autooam.whirr.whirrconf import WhirrConfigWriter
import emtools.common.utils as utils
from emapi import EnterpriseManagerAPI
from emtools.cluster.basecluster import BaseCluster
import emvmgr

Log = logutils.getLogger(__name__)

class Cluster(BaseCluster):

    def __init__(self, name, configspec, cid, machines = None, chefmode = True, attach = False):
        '''Constructor.
        
        @param name - name for the cluster (ideally unique)
        @param configspec - reference to a ConfigSpec object
        @param cid - unique id allocated to the cluster
        @param machines - [optional] map with instantiated machine info
        '''
        super(Cluster, self).__init__(name, configspec, machines=machines, chefmode=chefmode)

        # check to see if an EM is in use and set self._emapi accordingly
        if self.config()['em'] and self.config()['em']['present']:
            self._emapi = EnterpriseManagerAPI(self.config()['em']['emhost'], self.config()['em']['emport'], name)

            # populate the special "cluster" case where we match the em boxtype with the rest of the cluster
            if self.config()['em'].has_key('boxtype') and self.config()['em']['boxtype'] == "cluster":
                self.config()['em']['boxtype'] = self.config()['boxtype']

            # if we are installing the EM we want to go ahead and retrieve the version information
            # so that it is part of the run reporting
            if common.props['vmi.vagrantvmi.unit-test']:
                self.config()['em']['version'] = 'em-unit-test'
            elif self.config()['em']['invm'] and not attach:
                # if version is Latest and we are creating instead of attaching, then
                # go ahead and retrieve the EM package we will need.  This is important
                # so that the EM version is set after the constructor returns
                Log.info('Retrieving EM version %s...' % self.config()['em']['version'])
                vmgr = emvmgr.EMVersionManager()
                pkgtype = vagboxes.get_default_pkgtype(self.config()['em']['boxtype'])
                (emversion, pkgfile) = vmgr.retrieve(self.config()['em']['version'], pkgtype)
                self.config()['em']['version'] = emversion
            elif not attach:
                # this means we are point to an existing EM, insert the hostname as the version
                self.config()['em']['version'] = self.config()['em']['emhost']
        else:
            self._emapi = None
        self._id = cid

        # moved this validation from configspec to here,
        # because it only applies to autooam usage.
        if self._config['hadoop']:
            if not self._config['hadoop'].has_key('instance-templates'):
                Log.error('Must specify instance-templates when using hadoop')
                raise Exception("Must specify instance-templates when using hadoop")

    def id(self):
        """Returns the id."""
        return self._id

    def emapi(self):
        """Returns the EnterpriseManagerAPI instance."""
        return self._emapi

    def vmi(self, vmi):
        """Sets the VMI instance."""
        self._vmi = vmi
        
    def get_vmi(self):
        """Returns the VMI instance."""
        return self._vmi

    def get_pkgfile(self):
        """Returns pkg file name"""
        return self._vmi._pkgfile

    def get_rundir(self):
        """Returns runtime directory"""
        return self._vmi._rundir

    def get_upgfile(self):
        """Returns upgrade pkg file name"""
        return self._vmi._upgfile

    def get_pkgdir(self):
        """Returns cache package directory"""
        return common.props['vmi.versionmgr.packagedir']

    def get_extra_playbook_dir(self):
        """Returns extra playbook template directory"""
        return common.props['cluster.cluster.extra_playbook_templatedir']

    def get_sshkey_text(self):
        """Returns sshkey text (to be stored in ansible.cfg)"""
        f = open( common.props['vmi.vagrantvmi.sshkey'] )
        keytext = ''.join(f.readlines())
        return keytext

    def get_postconfig_opts(self):
        """Returns cmd line options to be passed to postConfigure"""
        if self.config()['idbuser'] == 'root':
            postconfig_opts = "-p qalpont!"
        else:
            postconfig_opts = "-p infinidb"
        if self.config()['pm_query']:
            postconfig_opts += " -lq"
        return postconfig_opts
    
    def jsonmap(self):
        """Returns a JSON encoding of the entire cluster."""
        return { u'name' : self._name,
                 u'config' : self._config.json_dumps(), 
                 u'vmi' : self._vmi.jsonmap(), 
                 u'machines' : self._machines }
    
    def status(self):
        """Returns an aggregate status of the cluster.
        
        Return value is one of:
            'not created'       : cluster vms not created, pending call to 'vagrant up'
            'poweroff'          : cluster vms created, but all powered off
            'partially created' : some vms created, some not - possible if there is an in progress 'vagrant up'
            'partially up'      : all vms created, some up, some not - could be interim startup state or intentional during test execution
            'running'           : all vms running
        """
        return self._vmi.status()
        
    def start(self):
        """Starts the cluster initially.  This method is intended to be called only once"""
        return self._vmi.start()

    def poweron(self, role=None):
        """Power on one or more nodes.  If role=None, then all power on"""
        return self._vmi.poweron(role)

    def poweroff(self, role=None):
        """Power off one or more nodes.  If role=None, then all power off"""
        return self._vmi.poweroff(role)

    def pause(self):
        """Pause the cluster (saves state and stops)"""
        return self._vmi.pause()

    def resume(self):
        """Resume the cluster after a pause"""
        return self._vmi.resume()

    def destroy(self):
        """Destroys the cluster and all file system artifacts related to the cluster.  DESTRUCTIVE operation."""
        if self._emapi:
            self._emapi.delete()
        return self._vmi.destroy()

    def destroy_files_only(self):
        """Destroys local file system artifacts only; useful in cleaning up unit tests.  DESTRUCTIVE operation."""
        return self._vmi.destroy_files_only()

    def shell_command(self, role, cmd, calpontbin=False, polling=False, timeout=-1):
        """Runs a shell commnd on the specified cluster node using ssh."""
        if calpontbin:
            cmd = '%s/bin/%s' % (self._config.infinidb_install_dir(), cmd)
        return self._vmi.shell_command(role, cmd, polling=polling, timeout=timeout)
        
    def calpont_console_cmd(self, cmd):
        """Issues a calpont console command on pm1."""
        cmd_ = '%s/bin/calpontConsole %s' % (self._config.infinidb_install_dir(), cmd)
        return self.shell_command('pm1', cmd_)

    def run_install_recipe(self, cb=None):
        """Run the proper install recipe from the autooam cookbook."""
        ret = 0
        # skip whirr hadoop install if we are running in unittest mode
        if not common.props['vmi.vagrantvmi.unit-test']:
            if self._config['hadoop']:
                if cb:
                    cb('Whirr Hadoop install Step')
                Log.info('Executing whirr launch-cluster for Hadoop')
                w = WhirrConfigWriter( self )
                w.write_config( self._vmi._rundir )
                owd = os.getcwd()
                os.chdir(self._vmi._rundir)
                cmd = '%s/whirr launch-cluster --config hadoop.properties --private-key-file %s/insecure_private_key' %\
                    (common.props['cluster.cluster.whirrdir'], common.props['vmi.vagrantvmi.vagrantroot'])
                ret = utils.syscall_log(cmd, self._vmi._outfile)[0]
                os.chdir(owd)
            
                # we also need to install libhdfs before moving on to the InfiniDB install
                if ret == 0:
                    if cb:
                        cb('Chef autooam::hadoop_postinstall Step')
                    # must be done on every InfiniDB node!
                    # TODO: consider moving this to an ansible playbook
                    for m in self._machines.keys():
                        if not m == "em1":
                            if ( vagboxes.get_os_family(self._config['boxtype']) == 'ubuntu' or\
                                 vagboxes.get_os_family(self._config['boxtype']) == 'debian' ):
                                cmd = 'sudo apt-get -y install libhdfs0'
                            else:
                                cmd = 'sudo yum -y install hadoop-libhdfs'
                            
                            ret = self.shell_command(m, cmd)

                            if ret != 0:
                                break

                if ret != 0:
                    Log.error('There were errors during Hadoop installation, did not attempt InfiniDB install')
                    return ret

        if cb:
            cb('InfiniDB install Step')
        Log.info('Performing InfiniDB install')
        recipe = 'autooam::binary_install' if self._config['binary'] else 'autooam::package_install'

        # Use EM to install Infinidb
        if self._emapi and common.props['cluster.cluster.use_em_for_dbinstall']:
            # Install EM (if applicable)
            ret = self._em_install(cb)
            if ret != 0:
                return ret

            # install db step
            ret = self._em_installdb(cb)

        # Install Infinidb through execution of ansible playbooks
        else:
            if self._chefmode:
                ret = self._run_chef_recipe(recipe)
            else:
                ret = self._run_ansible_playbook(recipe)
            if ret != 0:
                Log.error('There were errors installing InfiniDB')
                return ret

            if self._emapi:
                # Install and attach to EM (if applicable)
                ret = self._em_install(cb)
                if ret != 0:
                    return ret
                
                ret = self._em_attach( cb=cb )

        return ret

    def run_upgrade_recipe(self):
        """Run the proper upgrade recipe from the autooam cookbook."""
        if not self.config()['upgrade']:
            Log.warn('No upgrade version specified in ConfigSpec!')
            return 1
        recipe = 'autooam::binary_upgrade' if self._config['binary'] else 'autooam::package_upgrade'
        if self._chefmode:
            return self._run_chef_recipe(recipe)
        else:
            return self._run_ansible_playbook(recipe)

    def _run_chef_recipe(self, recipe, role='pm1'):
        """Run the proper recipe from the autooam cookbook."""
        # this is a little ugly.  Current we use two base boxes that came from Vagrant
        # whereas the rest are built by veewee.  Most of the veewee boxes put ruby
        # one place whereas the Vagrant boxes put it somewhere else.  The centos58
        # veewee box is unique too.
        # TODO: this doesn't work with our new boxes.  They don't like/need the ruby
        # part out in front of chef-solo.  When thef is pruned, this should also
        # be pruned.
        if ( vagboxes.get_os_family(self._config['boxtype']) == 'ubuntu' and
             eval(vagboxes.get_os_version(self._config['boxtype'])) < 14.04 ):
            ruby_path = '/opt/vagrant_ruby/bin'
        elif( self._config['boxtype'] == 'cal-centos58' ):
            ruby_path = '/usr/local/bin'
        else:
            ruby_path = '/usr/bin'
        cmd_ = 'sudo %s/ruby %s/chef-solo -c /tmp/vagrant-chef-*/solo.rb -j /tmp/vagrant-chef-*/dna.json -o %s' % (ruby_path, ruby_path, recipe)
        return self.shell_command(role, cmd_)

    def _run_ansible_playbook(self, recipe):
        """Run the proper recipe (playbook) from the autooam cookbook."""
        if (recipe == 'autooam::package_install'):
            playbookname = 'pkginstall'
        elif (recipe == 'autooam::package_upgrade'):
            playbookname = 'pkgupgrade'
        elif (recipe == 'autooam::binary_install'):
            playbookname = 'bininstall'
        else:
            playbookname = 'binupgrade'
        p = PlaybookInstall(self, playbookname)
        rc, results, out, err = p.run_cmd()
        if rc != 0:
            return rc;

        # Bug 5967: SIGHUP work-around; restart infiniDB after installation
        #           This restartsystem can/should be removed if we can
        #           resolve the nagging SIGHUP that is causing us to lose
        #           the controllernode/workernode connection on PM1 after
        #           an installation performed through an ansible playbook.
        if not self.config()['em'] or not self.config()['em']['present']:
            Log.info('Restarting InfiniDB after install')
            rc = self.shell_command('pm1', 'calpontConsole restartsystem y', calpontbin=True)
            if rc != 0:
                Log.error('There were errors restarting InfiniDB after install')
                return rc

        return 0

    def _em_install(self, cb=None):
        """Install EM on EM server"""
        if self._config['em']['invm']:
            # we are using a VM so the em needs to be installed.
            if cb:
                cb('EM install Step')
            import autooam.cluster.eminstall as eminstall
            emi = eminstall.EMInstall(self)
            ret = emi.run_cmd()
            if ret != 0:
                Log.error('There were errors installing the EM')
                return ret

        return 0

    def _em_attach(self, emhost=None, emport=None, oamserver_role=None, cb=None):
        """Attach to EM Server"""
        if cb:
            cb('EM attach Step')

        if not emhost:
            emhost = self.config()['em']['emhost']
        if not emport:
            emport = self.config()['em']['emport']
        if not oamserver_role:
            oamserver_role = self.config()['em']['oamserver_role']
            
        Log.info('Attaching to EM server %s' % emhost)
        # we'll re-instantiate the emapi since someone could have passed in different emhost/emport
        self._emapi = EnterpriseManagerAPI(emhost, emport, self.name())
        um1 = self.machine(oamserver_role)
        # TODO-VMI should support a credentials() method or equivalent
        rc = self._emapi.attach(self,um1['hostname'], um1['hostname'],'vagrant', common.props['vmi.vagrantvmi.sshkey'])
        if rc != 0:
            Log.error('There were errors attaching to EM after installing InfiniDB')
            return rc
        
        # TODO - use em API to restart when available
        if cb:
            cb('Restart for query telemetry/startup issue Step')

        # need to restart the system to active query telemetry
        Log.info('EM attach successful, restarting to activate query telemtry')
        rc = self.shell_command('pm1', 'calpontConsole restartsystem y', calpontbin=True)
        if rc != 0:
            Log.error('There were errors restarting InfiniDB after installation')

        return rc

    def _em_installdb(self, cb=None):
        """Use EM Server to install Infinidb"""
        if cb:
            cb('EM Install of DB Step')

        emhost = self.config()['em']['emhost']
        emport = self.config()['em']['emport']
        oamserver_role = self.config()['em']['oamserver_role']

        Log.info('Using EM to install InfiniDB')
        # we'll re-instantiate the emapi since someone could have passed in different emhost/emport
        self._emapi = EnterpriseManagerAPI(emhost, emport, self.name())
        # TODO-VMI should support a credentials() method or equivalent
        rc = self._emapi.installdb(self, common.props['vmi.vagrantvmi.sshkey'])
        if rc != 0:
            Log.error('There were errors using EM to install InfiniDB')
            return rc

        return rc
