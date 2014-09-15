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
autooam.vmi.vagrantvmi

Concrete VMI type capable of interacting with Vagrant/VirtualBox
'''
import os
import time
import emtools.common as common
import emtools.common.utils as utils
import shutil
from datetime import datetime
from emtools.cluster.postcfg import PostConfigureHelper
from vagsubnet import VagrantSubnetAlloc
from vagfile import VagrantFileWriter
import autooam.testlib.vagboxes as vagboxes
import vagstatus
from versionmgr import VersionManager
import json

from emtools.cluster.configspec import ConfigSpec
import emtools.common.logutils as logutils
Log = logutils.getLogger(__name__)

class VagrantVMI(object):
    '''
    VagrantVMI is a concrete VMI class for interacting with a vagrant
    installation to create and run virtual machine clusters
    '''

    def __init__(self, cluster, vmi=None):
        '''
        Constructor
        '''
        self._cluster = cluster
        self._salloc = VagrantSubnetAlloc()
        self._sshkey = common.props['vmi.vagrantvmi.sshkey']       
        if vmi:
            return self._attach_construct(cluster, vmi)
        else:
            return self._alloc_construct(cluster)
                
    def _attach_construct(self, cluster, vmi):
        '''attach to a previously created vmi instance, typically loaded out of mongodb.'''
        self._rundir = vmi['rundir']
        self._vfile = vmi['vfile']
        self._pfile = vmi['pfile']
        self._outfile = vmi['outfile']
        self._subnet = vmi['subnet']
        # really only need to check vfile and pfile since they exist below rundir
        if not os.path.exists(self._vfile) or not os.path.exists(self._pfile):
            raise Exception("Unable to properly attach - missing all or part of %s" % self._rundir)
        # Verify existence of DBRoot paths we will export for external storage
        if cluster.config()['storage'] == 'external':
            rootCount = cluster.config().total_dbroot_count()
            for i in range( rootCount ):
                dbRootDir = '%s/data%d' % (self._rundir, i+1)
                if not os.path.exists( dbRootDir ):
                    raise Exception("Unable to properly attach - DBRoot %s is missing" % dbRootDir)
        
        cluster.vmi(self)
        
    def _alloc_construct(self, cluster):
        '''create a new vmi instance.'''
        if not cluster.config().has_key('boxtype'):
            raise Exception("Vagrant cluster creation requires a boxtype in the ConfigSpec")

        # this hadoop validation check was formerly in configspec, but
        # moved to here to remove autooam/vagboxes dependency from
        # emtools/configspec
        if cluster.config().has_key('hadoop') and cluster.config()['hadoop']:
            if not vagboxes.hadoop_support(cluster.config()['boxtype']):
                raise Exception("Hadoop not supported on boxtype %s" % self.jsonmap['boxtype'])

        self._subnet = self._salloc.alloc(cluster)
        
        # first we want to look for our root directory, make sure it
        # does not already exist and then create it
        root = common.props['vmi.vagrantvmi.vagrantdir']
        utils.mkdir_p(root)        
        self._rundir = '%s/%s_%s' % (root, cluster.name(), str(cluster.id()))
        os.makedirs(self._rundir)

        # this is where we will write stdout and stderr for any calls
        # executed agaist this VMI
        self._outfile = "%s/%s.out" % (self._rundir, cluster.name())
        
        self._defmemsize = common.props['vmi.vagrantvmi.defmemsize']
        self._defcpus = common.props['vmi.vagrantvmi.defcpus']
        
        # do a sanity check to make sure we don't ask for a non-existent package
        # we only support enterprise=False for versions 4.0 and later
        entpkg = cluster.config()['enterprise']
        if ConfigSpec._version_greaterthan('4.0.0-0',cluster.config()['idbversion']):
            Log.info('resetting enterprise to True for version %s ' % cluster.config()['idbversion'])
            entpkg = True
            
        # make sure that our package exists
        vm = VersionManager()
        if cluster.config()['idbuser'] != 'root' or cluster.config()['binary']:
            ptype = 'binary'
            # set this to true in case not already set so that vagrant file writer
            # can depend on it being accurate
            cluster.config()['binary'] = True
        else:
            ptype = vagboxes.get_default_pkgtype(cluster.config()['boxtype'])
        self._pkgfile = vm.retrieve(cluster.config()['idbversion'], ptype, enterprise=entpkg)
        
        # handle the upgrade version if the user specified it
        upgfile = None
        upgvers = None
        if cluster.config()['upgrade']:
            upgfile = vm.retrieve(cluster.config()['upgrade'], ptype, enterprise=entpkg)
            upgvers = vm.get_pkg_version(upgfile)
        self._upgfile = upgfile
            
        # handle datdup package if the user requested it - note that the datdup
        # package is only relevant prior to version 4.0
        datduppkgfile = None
        if cluster.config()['datdup'] and not ConfigSpec._version_greaterthan(cluster.config()['idbversion'],'4.0.0-0'):
            datduppkgfile = vm.retrieve(cluster.config()['idbversion'], ptype, datdup=True)
        
        self._alloc_machines()
        
        h = PostConfigureHelper()
        self._pfile  = '%s/postconfigure.in' % self._rundir
        h.write_input(self._pfile, cluster, ptype)
 
        # @bug 5990: don't need to copy public key.  vagrant
        # public access should already be setup when cluster
        # was instantiated.
        # copy public key to shared directory so that vagrant can access
        #utils.mkdir_p("%s/.ssh" % self._rundir)
        #shutil.copy( '%s.pub' % common.props['emtools.test.sshkeyfile'],
        #    '%s/.ssh/public_key' % self._rundir)

        self._vfile = self._rundir + '/Vagrantfile'
        vfile = VagrantFileWriter(
                    cluster, 
                    self._pkgfile,
                    vm.get_pkg_version(self._pkgfile),
                    datduppkgfile, 
                    self._upgfile,
                    upgvers,
                    self._subnet,
                    self._rundir)
        vfile.writeVagrantFile( self._vfile )
        cluster.vmi(self)

        # For external DBRoot storage: delete/recreate dataN directories
        # locally, to be NFS mounted for use on each PM
        if cluster.config()['storage'] == 'external':
            rootCount = cluster.config().total_dbroot_count()
            for i in range( rootCount ):
                dbRootDir = '%s/data%d' % (self._rundir, i+1)
                if os.path.exists( dbRootDir ):
                    shutil.rmtree( dbRootDir )
                os.mkdir( dbRootDir )

    def jsonmap(self):
        '''return a JSON formatted string to persist that object.'''
        return { 
                u'vmitype' : 'vagrant', 
                u'subnet' : self._subnet, 
                u'rundir' : self._rundir, 
                u'vfile' : self._vfile, 
                u'pfile' : self._pfile,
                u'outfile' : self._outfile }
    
    def start(self):
        if common.props['vmi.vagrantvmi.unit-test']:
            # if we are running in unit test mode, simulate a start by creating the .vagrant file
            f = open("%s/.vagrant" % self._rundir,'w')
            f.write('{"active" : {')
            first = True
            for m in self._cluster.machines():
                if not first:
                    f.write(',') 
                f.write('"%s":"0e18cd55-ee19-414d-a874-3cfee1a9df5b"' % m)
                first = False
            f.write('}}')
            f.close()
        else:
            # if we are not running in unit-test mode here then we want to check to make
            # sure the user has exported their AUTOOAM_HOME so that it can be mounted by
            # the cluster
            cmd = 'grep "%s" /etc/exports' % os.environ['AUTOOAM_HOME']
            ret = utils.syscall_log(cmd)
            if ret[0] != 0:
                Log.error("no NFS export for $AUTOOAM_HOME")
                print "You need to execute the following commands:"
                print "    sudo bash -c \"echo '%s 192.168.0.0/255.255.0.0(rw,sync,all_squash,no_subtree_check,anonuid=%d,anongid=%d)' >> /etc/exports\"" % (os.environ['AUTOOAM_HOME'],os.getuid(),os.getgid())
                print "    sudo exportfs -a"
                raise Exception('Fatal error - NFS export not configured')

        # our cal-centos58 is excessively slow to boot
        base_timeout = 180 if self._cluster.config()['boxtype'] != 'cal-centos58' else 300
        # multiply base times # of nodes since vagrant starts sequentially
        ctimeout = base_timeout * len(self._cluster.machines())
        return self._vagrant_call('vagrant --parallel up',timeout=ctimeout)

    def pause(self):
        """Pause the cluster (saves state and stops)"""
        return self._vagrant_call('vagrant suspend')

    def resume(self):
        """Resume the cluster after a pause"""
        return self._vagrant_call('vagrant resume')

    def destroy(self):
        if not os.path.exists(self._rundir):
            Log.warning("Cluster run directory %s does not exist!" % self._rundir)
            return -1

        ret = 0
        status = vagstatus.vagrant_status(self._rundir)
        if status['cluster'] != 'not created':
            ret = self._vagrant_call('vagrant destroy -f')

        shutil.rmtree(self._rundir)
        return ret

    def destroy_files_only(self):
        if not os.path.exists(self._rundir):
            Log.warning("Cluster run directory %s does not exist!" % self._rundir)
            return -1

        shutil.rmtree(self._rundir)
        return 0
        
    def _vboxmanage(self, op, args, role, retrycnt=3):
        '''
        This method makes one or more calls to vboxmanage of the form:
            vboxmanage <op> <vm uuid> <args>
        
        Parameters are as follows:
        @param op    - vboxmanage operation to issue (see template call above)
        @param args  - additional arguments to pass (see template call above)
        @param role  - optional argument - if None then issue one command
                       for each node in the cluster, otherwise issue a single
                       command to the named node
        @param retrycnt - optional argument - specifies how many times the
                       command should be retried before aborting.  VirtualBox
                       is sensitive of timing of various operations so just 
                       because it failed the first time is not necessarily 
                       indicative of a real failure 
        '''
        vagstat = '%s/.vagrant' % self._rundir
        if not os.path.exists(vagstat):
            Log.error("cluster not created - %s does not exist" % vagstat)
            return -1
        
        vsfile = open(vagstat)
        vs = json.load(vsfile)
        if role:
            if not vs['active'].has_key(role):
                raise Exception("role %s does not exist" % role)
            affected_roles = [ role ]
        else:
            affected_roles = sorted(vs['active'].keys())

        ret = 0            
        for r in affected_roles:
            cmd = 'vboxmanage %s %s %s' % (op, vs['active'][r], args)
            tmp = self._syscall(cmd, retrycnt=retrycnt, retrywait=1)
            # the vboxmanage command does not seem to like back-to-back 
            # commands so sleep for 1
            utils.sleep(1)

            if tmp != 0:
                ret = tmp
        return ret                
        
    def poweroff(self, role, timeout=20):
        """Power off one or more nodes in the cluster."""
        
        # spent much trial-and-error figuring out the best way to do this.
        # the vboxmanage controlvm ... poweroff option is tempting but 
        # problematic because it loses state - specifically files recently
        # written are missing once it starts up again (this tended to 
        # clobber Calpont.xml on pm1).  Also tried acpipowerbutton which
        # may work with properly configured vms, but did nothing on our
        # default boxes.  I then tried issuing 'shutdown' commands to each
        # node and monitoring the state until poweroff - this had better
        # success but still only in the 70-80% range.  In the end, the most
        # reliable thing I have found is vagrant halt so sticking with that.
        # the only negative to this approach is the vagrant halt shuts down
        # each machine sequentially and thus takes a bit longer than something
        # operating on multiple machines in parallel
        if not role:
            return self._vagrant_call('vagrant halt')
        else:
            return self._vagrant_call('vagrant halt %s' % role)
        
    def poweron(self, role):
        """Power on one or more nodes in the cluster."""
        try:
            # Note - theoretically, 'vagrant up' is an equivalent option here
            # but intentionally doing this through vboxmanage for two reasons.
            # First, vboxmanage operates serially across each machine so startup
            # time will grow linearly with the size of the cluster.  Second,
            # vagrant up reruns all of the Chef provisioning.  Technically, this
            # should be ok since all of the Chef recipes autooam uses are set up
            # to preserve state, but still it is deemed more realistic to not
            # rerun them and force the machine to boot up with whatever state is
            # present. 
            
            # TODO - this is a big hack around the real work that needs to be
            # done for the Vagrant upgrade.  They changed their status from 
            # a simple JSON file to a directory structure.  
            if os.path.isdir( '%s/.vagrant' % self._rundir ):
                return self._vagrant_call('vagrant --parallel up')
                
            return self._vboxmanage('startvm', '--type headless', role)
        except Exception as exc:
            import traceback
            raise Exception("Could not poweron: %s" % traceback.format_exc())
        
    def status(self):
        '''Returns the status for the cluster.  See vagstatus module for details.'''
        return vagstatus.vagrant_status(self._rundir)['cluster']        
        
    def shell_command(self, role, cmd, polling=False, timeout=-1):
        """Run a command on a particular machine on the cluster.
        
        Assumed that paswordless ssh for the current user into the machine.
        Throws an exception if the role does not exist in the cluster.
        TODO: will need a timeout of some kind (i.e. how long do I wait for the
        command to finish before I give up) 
        """
        user = 'root'
        if self._cluster.config().has_key('idbuser'):
            user = self._cluster.config()['idbuser']

        find_this = "/mnt/autooam"
        if find_this in cmd:
            if user == 'root': 
                cmd = 'mount -a;' + cmd
            else:
                cmd = 'sudo mount -a;' + cmd

        cmd = "ssh -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i %s %s@%s '%s'" % \
            (self._sshkey,user,self._cluster.machine(role)['ip'], cmd)
        return self._syscall(cmd, polling=polling, timeout=timeout)

    def _vagrant_call(self, cmd, timeout=-1):
        '''make a vagrant system call, must make sure we issue from the vagrant directory.'''
        owd = os.getcwd()
        os.chdir(self._rundir)
        ret = self._syscall(cmd,timeout=timeout)
        os.chdir(owd)
        return ret

    def _syscall(self, cmd, retrycnt=1, retrywait=1, timeout=-1, polling=False):
        '''issue a system call.'''
        if not polling:
            Log.info('Executing: %s' % cmd)
        ret = 1
        attempts = 0
        while ret and attempts < retrycnt:
            attempts += 1 
            ret = utils.syscall_log(cmd, self._outfile, timeout=timeout)[0]
            if ret:
                if not polling:
                    Log.error('%s returned %d' % (cmd, ret))
                if attempts < retrywait:
                    utils.sleep(retrywait)            
        return ret
                    
    def _alloc_machines(self):
        '''use the rolespec in the 'config' section to create the set of machines.'''
        cfg = self._cluster.config()        
        
        # vagrant/virtualbox reserves ip address 1 for the host
        self._next_ip = 2
        
        # pms first, guaranteed to exist with a non-zero count
        self._alloc_role('pm', cfg['rolespec']['pm'])
        
        if( cfg['rolespec'].has_key('um')):
            self._alloc_role('um', cfg['rolespec']['um'])

        if( cfg['em'] and cfg['em']['present'] and cfg['em']['invm']):
            # this option tells us to allocate a vm and then update the emhost            
            emrole = cfg['em']['role'] 
            if emrole == 'em1':
                self._alloc_role('em', { "count" : 1 } )
                
            cfg['em']['emhost'] = self._cluster.machine(emrole)['hostname']
            
    def _alloc_role(self, role, rolespec):
        rolect = 1
        for i in range(0, rolespec['count']):
            ip = '%s.%d' % (self._subnet, self._next_ip)
            name = '%s%d' % (role,rolect)
            mach = { "ip" : ip }
            # we are going to make a deterministic hostname from the ip address
            # by substituting _ for .
            hostname = ip.replace('.','-')
            mach['hostname'] = hostname
            
            if role == 'pm':
                dbroots = []
                if rolespec.has_key('dbroots_per'):
                    per = rolespec['dbroots_per']
                    for j in range(1, per + 1):
                        dbroots.append(j+((rolect - 1) * per))
                else:
                    dbroots = rolespec['dbroots_list']
                mach['dbroots'] = dbroots
                
            if rolespec.has_key('memory'):
                mach['memory'] = rolespec['memory']
            else:
                mach['memory'] = self._defmemsize

            if rolespec.has_key('cpus'):
                mach['cpus'] = rolespec['cpus']
            else:
                mach['cpus'] = self._defcpus            

            self._cluster.add_machine(name, mach)
            
            rolect = rolect + 1
            self._next_ip = self._next_ip + 1
