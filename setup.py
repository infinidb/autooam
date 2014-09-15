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

# install mongodb - this link has good instructions for ubuntu
# https://www.digitalocean.com/community/articles/how-to-install-mongodb-on-ubuntu-12-04
# pip install pymongo
# pip install jprops
#
# handle vagrant install - this should be optional depending on whether this is dev or run-time
# script TBD
#
# handle package area mount
# sudo mount -t cifs -o user=oamuser,password=Calpont1 //calweb/shared /media/packages
# as fstab entry:
# //calweb/shared  /media/packages  cifs  username=oamuser,password=Calpont1  0  0
#
import os,sys

# if this is truly first time, the user may not have ever set this
if not os.environ.has_key('AUTOOAM_HOME'):
    os.environ['AUTOOAM_HOME'] = os.getcwd()

import autooam.testlib.vagboxes as vagboxes
import emtools.common.logutils as logutils
Log = logutils.getLogger(__name__)

def list_boxes():
    boxes = []
    h = os.popen('vagrant box list')
    for line in h.readlines():
        b = line.strip()
        b = line.split()[0]
        if len(b):
            boxes.append(b)
    return boxes

if __name__ == "__main__":
    autooamdir = os.getcwd()
    homedir    = os.environ['HOME']
    
    print 'This script will assist you in setting up your environment to run autooam.'
    print ''
    if not os.path.exists('setenv'):
        print ''
        print 'You don\'t have a setenv script, I will create one for you...'
        print 'This script sets several environment variables including:' 
        print '    AUTOOAM_HOME'
        print '    PYTHONPATH'
        print '    PATH'
        print 'You will need to source this file each time you login.  We don\t'
        print 'set these globally in .bashrc so that we can share one account on an'
        print 'autooam machine with different users.  The command will look like this:'
        print '    . ./setenv'
        print ''
        f = open('setenv','w')
        f.write('''#!/bin/bash
ANSIBLE_HOME=%s/ansible
export AUTOOAM_HOME=%s
export INFINIDB_EM_TOOLS_HOME=%s/infinidb-em-tools
export ANSIBLE_LIBRARY=$INFINIDB_EM_TOOLS_HOME/share/infinidb:$ANSIBLE_HOME/library
export PYTHONPATH=$AUTOOAM_HOME:$INFINIDB_EM_TOOLS_HOME:$ANSIBLE_HOME/lib:$PYTHONPATH
export PATH=$PATH:/opt/vagrant/bin:$ANSIBLE_HOME/bin
''' % (homedir,autooamdir,homedir))
        f.close()
        os.chmod('setenv',0755)
    else:
        print 'You already have a setenv script.  Skipping this step.'
    
    print ''
    print 'The rest of the setup steps are only applicable if you are on a machine'
    print 'where you intend to actually run the framework (as opposed to develop and'
    print 'unit test.'
    print ''
    print 'Do you want to continue? (y) ',
    ans = sys.stdin.readline().strip().lower()
    if ans != 'n':
        print ''
        print 'NOTE: you will need sudo access and may be prompted for your sudo password.'
        print ''
        print 'First we will check to see if you need to install the /opt/autooam area'
        
        if not os.path.exists('/opt/autooam'):
            os.system('sudo mkdir /opt/autooam')
        if not os.path.exists('/net/srvengcm1/Calpont/exports/autooam'):
            print 'ERROR - it looks like automount of /net/srvengcm1 is not setup.  Contact your admin.'            
        else:
            print 'Copying files from /net/srvengcm1/Calpont/exports/autooam.  This may take awhile...'
            os.system('sudo rsync -av /net/srvengcm1/Calpont/exports/autooam /opt')

        print 'Next we will check your NFS export of this autooam directory.'
        if not os.path.exists('/etc/exports'):
            print 'ERROR - it looks like NFS is not setup on this machine.  Contact your admin'
        else:
            ret = os.system('grep %s /etc/exports > /dev/null 2>&1' % autooamdir)
            ret = ret >> 8
            if ret != 0:
                ret1 = os.system('sudo bash -c "echo \'%s 192.168.0.0/255.255.0.0(rw,sync,all_squash,no_subtree_check,anonuid=%d,anongid=%d)\' >> /etc/exports"' % (autooamdir,os.getuid(),os.getgid())) >> 8
                ret2 = os.system('sudo exportfs -a') >> 8
                if ret1 or ret2:
                    print 'ERROR - unable to add AUTOOAM_HOME NFS export'
                else:
                    print 'Your AUTOOAM_HOME NFS export is now configured.'
            else:
                print 'Your AUTOOAM_HOME NFS export is already configured.'

            ret = os.system('grep /opt/autooam /etc/exports > /dev/null 2>&1')
            ret = ret >> 8
            if ret != 0:
                ret1 = os.system('sudo bash -c "echo \'/opt/autooam 192.168.0.0/255.255.0.0(ro,sync,all_squash,no_subtree_check,anonuid=%d,anongid=%d)\' >> /etc/exports"' % (os.getuid(),os.getgid())) >> 8
                ret2 = os.system('sudo exportfs -a') >> 8
                if ret1 or ret2:
                    print 'ERROR - unable to add /opt/autooam NFS export'
                else:
                    print 'Your /opt/autooam NFS export is now configured.'
            else:
                print 'Your /opt/autooam NFS export is already configured.'
    
        print ''
        print 'Next we will check to see if you need to install any vagrant boxes'
        
        rc = os.system('which vagrant') >> 8
        if rc != 0:
            print 'ERROR - it looks like vagrant is not setup on this machine.  Contact your admin'
        else:
            these_boxes = list_boxes()
            need_to_update = []
            for b in vagboxes.list_all():
                if not b in these_boxes:
                    need_to_update.append(b)
                
            if len(need_to_update):
                print "You are missing one or more vagrant boxes, would you like to install(this may take awhile...)? (y) ",
                ans = sys.stdin.readline().strip().lower()
                if ans != 'n':
                    for b in vagboxes.list_all():
                        try:
                            these_boxes.index(b)
                            print 'Skipping %s, already installed.' % (b)
                        except:
                            print 'Will install box %s.' % (b)
                            boxrepo = '/net/srvengcm1/Calpont/exports/vagrant_boxes'
                            if not os.path.exists(boxrepo):
                                Log.error("Cannot access the box repository at %s, make sure automount is set up!" % boxrepo)
                                sys.exit(-1)
                            cmd = "vagrant box add %s %s/%s.box" % (b, boxrepo, b)
                            Log.debug(cmd)
                            os.system( cmd )
            else:
                print "All vagrant boxes are installed"

        print '' 
        print 'Setup Finished!'
