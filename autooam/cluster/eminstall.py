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
autooam.cluster.eminstall

contains:
    class EMInstall
'''
import os
#dmc logging conflict between autooam and emtools
#    import emtool.playbookmgr before autooam.common.logutils
#    to insure that logutils is configured for autooam.
from emtools.playbookmgr import PlaybookMgr
import emtools.common.logutils as logutils
import emtools.common as common
from autooam.vmi.versionmgr import VersionManager
import autooam.testlib.vagboxes as vagboxes
import emvmgr

Log = logutils.getLogger(__name__)

class EMInstall(object):
    '''
    Generate/executes ansible playbook for EM install.
    '''

    def __init__(self, cluster):
        '''
        Constructor
        '''
        self._cluster = cluster
 
    def run_cmd(self):
        '''
        Prepare and run the ansible playbook command for
        the operation type specified in the constructor
        '''
        self._rundir  = self._cluster.get_vmi()._rundir
        emboxtype = self._cluster.config()['em']['boxtype']
        if not vagboxes.em_support(emboxtype):
            # Don't even try to install if the boxtype does not support an EM
            print 'supported is %s' % vagboxes.list_all(flags=vagboxes.FLAG_EM)
            Log.error("boxtype %s does not support the EM!" % emboxtype)
            return 1
        
        self._pkgtype = vagboxes.get_default_pkgtype(emboxtype)
        vmgr = emvmgr.EMVersionManager()
        (emversion, self._pkgfile) = vmgr.retrieve(self._cluster.config()['em']['version'], self._pkgtype)
        self._pkgname = os.path.split( self._pkgfile )[1]
        
        (ansible_yml,cmdargs) = self._prepare_playbook_install()

        extra_playdir = self._cluster.get_extra_playbook_dir()
        p = PlaybookMgr( os.path.basename(self._rundir), extra_playdir )

        # create ansible inventory file with list of hosts
        emrole = self._cluster.config()['em']['role']
        iplist = [ self._cluster.machine(emrole)['ip'] ]
        ipdict = { 'all' : iplist }
        p.write_inventory( 'emdefault', ipdict )

        # create ansible.cfg file
        self._idbuser = self._cluster.config()['idbuser']
        f = open( common.props['vmi.vagrantvmi.sshkey'] )
        keytext = ''.join(f.readlines())
        p.config_ssh( self._idbuser, keytext )

        # execute playbook thru PlaybookMgr
        Log.info("Running %s EM pkg install playbook; --extra-vars=%s" % (ansible_yml,cmdargs))
        rc, results, out, err = p.run_playbook(ansible_yml, 'emdefault', playbook_args=cmdargs)
        return rc

    def _prepare_playbook_install(self):
        """
        Prepare pkg install using ansible playbook.
        """
        playbook = ('%s/eminstall.yml' % self._rundir)
        cmdargs = ("\"pkgfile=%s "
                   "pkgname=%s \"" % (self._pkgfile, self._pkgname))

        return (playbook,cmdargs)

