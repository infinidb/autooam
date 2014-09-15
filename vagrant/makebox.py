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

#!/usr/bin/env python

import os,sys,getopt
from emtools.common.utils import syscall_log
from autooam.vmi.vagstatus import vagrant_status
import re

def usage():
    print '''usage: usage: makebox.py [-hlrb:ds]
    
    Options:
        -h        : show usage
        -l        : install new boxes locally
        -r        : install new boxes remote
        -b <box>  : process a singe named box (default = all subdirectories) 
        -d        : destroy box and start over (defaut = use existing box state)
        -s        : skip box creation. (NOTE: use this only if you are SURE the 
                                              .box files are already updated)
        -c        : check boxes only - this runs the playbook but does not 
                    write a new box
        
    basebox : initial box - can be remote or local
    boxname : new box to create
'''

def syscall(cmd):
    print 'INFO: issuing %s' % cmd
    (rc, out, err) = syscall_log(cmd)
    if rc != 0:
        raise Exception("Command %s failed! rc=%s, stdout=%s, stderr=%s" % (cmd, rc, out, err))
    return (rc, out, err)

def do_box(boxname, do_local = False, do_remote = False, do_destroy = False, do_skip = False, do_check = False):
    print 'INFO: Handling box %s' % boxname
    ret = 0
    cwd = os.getcwd()
    os.chdir(boxname)
    try:
        if not os.path.exists('Vagrantfile'):
            raise Exception("ERROR: no VagrantFile found in %s" % boxname)
        
        if not do_skip:
            if do_destroy:
                syscall('vagrant destroy -f')
            else:
                status = vagrant_status('.')
                if status['cluster'] != "not created" and status['cluster'] != "poweroff":
                    print "INFO: machine appears to be running or suspended, shutting down for clean restart"
                    syscall('vagrant halt') 
                
            (rc, out, err) = syscall('vagrant up')
            sshportpatt = re.compile('SSH address: 127.0.0.1:([0-9]+)')
            mat = sshportpatt.search( out )
            if not mat:
                raise Exception('ERROR: could not locate SSH address in %s' % out)
            sshport = mat.group(1)
            print 'INFO: vagrant box %s is on port %s' % (boxname, sshport)
    
            java_file = os.path.join('..','jdk-7u55-linux-x64.gz')
            syscall('cp %s .' % java_file)
            
            cmd = 'ansible-playbook -i ../inventory ../makebox.yml -e "ansible_ssh_port=%s boxdir=%s"' % (sshport,boxname)
            rc = os.system(cmd) >> 8
            if rc != 0:
                raise Exception("Ansible command (%s) failed: %s!" % (cmd, rc))
            
            syscall('vagrant halt')
            
            if not do_check:
                if os.path.exists('%s.box' % boxname):
                    os.remove('%s.box' % boxname)
                syscall('vagrant package --output %s.box' % boxname)

        if do_local:
            (rc, out, err) = syscall('vagrant box list')
            for b in out.split('\n'):
                box = b.split(' ')[0]
                if box == boxname:
                    syscall('vagrant box remove %s' % boxname)
                    break
                
            syscall('vagrant box add %s ./%s.box' % (boxname, boxname))
    
        if do_remote:
            print 'INFO: going to scp the new box to srvengcm1...this may prompt for a password'
            rc = os.system('scp %s.box root@srvengcm1.calpont.com:/Calpont/exports/vagrant_boxes/.' % (boxname)) >> 8
            if rc != 0:
                raise Exception("scp command failed: %s!" % (rc))
            
            
    except Exception, exc:
        print exc
        ret = 1

    os.chdir( cwd )
    return ret

def main(argv=None):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlrb:dsc", [])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    do_local = False
    do_remote = False
    do_destroy = False
    do_skip = False
    do_check = False
    boxname = None
    for o, a in opts:
        if o == "-h":
            usage()
            return 0
        elif o == "-l":
            do_local = True
        elif o == "-r":
            do_remote = True
        elif o == "-b":
            boxname = a
        elif o == "-d":
            do_destroy = True
        elif o == "-s":
            do_skip = True
        elif o == "-c":
            do_check = True
        else:
            assert False, "unhandled option"
                
    boxes = []
    if boxname:
        if not os.path.isdir(boxname):
            print 'ERROR: no subdircetory named %s' % boxname
            sys.exit(1)
        boxes.append( boxname )
    else:
        for p in os.listdir('.'):
            if os.path.isdir(p):
                boxes.append(p)
    print 'INFO: going to process boxes %s' % boxes

    for box in boxes:
        do_box( box, do_local=do_local, do_remote=do_remote, do_destroy=do_destroy, do_skip=do_skip, do_check=do_check )
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
