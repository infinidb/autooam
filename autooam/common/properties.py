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
autooam.common.properties

Overrides the base emtools Properties class with additional properties for autooam
'''
import os
import emtools.common.properties

class Properties(emtools.common.properties.Properties):
    def __init__(self, unittest = False):
        autooam_props = {
            'vmi.vagrantvmi.vagrantroot':      (str, '%s/.vagrant.d' % (os.environ['HOME'])),
            'vmi.vagrantvmi.vagrantdir':       (str, '%s/vagrantdir' % (os.environ['AUTOOAM_HOME'])),
            'vmi.vagrantvmi.defmemsize':       (int, 1024),
            'vmi.vagrantvmi.defcpus':          (int, 2),
            'vmi.vagrantvmi.calpontxmldir':    (str, '%s/examples' % (os.environ['AUTOOAM_HOME'])),
            'vmi.vagrantvmi.sshkey':(str, '%s/.vagrant.d/insecure_private_key' % (os.environ['HOME'])),
            'vmi.vagrantvmi.unit-test':        (bool, False),
        
            'vmi.versionmgr.basedir':          (str, '/media/packages/Iterations'),
            'vmi.versionmgr.packagedir':       (str, '%s/examples' % (os.environ['AUTOOAM_HOME'])),
        
            'cluster.configspec.basedir':      (str, '%s/config-spec' % (os.environ['AUTOOAM_HOME'])),

            'cluster.cluster.whirrdir':        (str, '%s/whirr-0.8.2/bin' % (os.environ['HOME'])),
            'cluster.cluster.extra_playbook_templatedir': (str,'%s/playbook_template' % (os.environ['AUTOOAM_HOME'])),
            'cluster.cluster.use_em_for_dbinstall': (bool, False),

            'cluster.emapi.timeout':           (int,  10),
            'cluster.emapi.debug':             (bool, False),
        
            'cluster.emvmgr.packagedir':       (str, '%s/em-packages' % (os.environ['AUTOOAM_HOME'])),
            'cluster.emvmgr.httpuser':         (str, 'bwilkinson'),
            'cluster.emvmgr.httppassword':     (str, 'Calpont1'),
        
            'common.oammongo.dbhost':          (str, 'localhost'),
            'common.oammongo.dbport':          (int, 27017),
            'common.oammongo.dbname':          (str, 'autooamdb'),
        
            'testsuite.testscript.basedir':    (str, '%s/test-script' % (os.environ['AUTOOAM_HOME'])),
            'testlib.runlists.upgradefrom':    (str, '2.2,3.0.6-3,3.5,3.6,4.0,4.5'),
            # If true then runlists will only generate configs using boxtypes supported be EM
            'testlib.runlists.embox_only':     (bool, False),
            
            'testmgr.testmgr.emaildist':       (str, 'bwilkinson@calpont.com,wweeks@calpont.com'),
            # If true then runlists will only generate configs using boxtypes supported be EM
            'testmgr.testmgr.pause_failed':    (bool, True),
        }
        
        autooam_site = os.path.join( os.environ['AUTOOAM_HOME'], 'conf', 'site.properties')
        emtools.common.properties.Properties.__init__(self, unittest = unittest, addtl_defns=autooam_props, addtl_site=autooam_site)
