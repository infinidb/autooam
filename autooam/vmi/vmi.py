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
autooam.vmi.vmi

An abstract base class for derived VMI types that know how to interact with a
particular virtualization technology. 
'''
from vagrantvmi import VagrantVMI
from ec2vmi import EC2VMI
from abc import ABCMeta, abstractmethod

class VMI(object):
    '''
    Abstract base class for autooam virtual machine interface
    '''
    
    @classmethod
    def Create(cls, ctype, cluster):
        '''Factory method that creates a new cluster.'''
        if ctype == 'vagrant':
            return VagrantVMI(cluster)
        elif ctype == 'ec2':
            return EC2VMI()
        
    @classmethod
    def Attach(cls, cluster, vmidefn):
        '''Factory method that attaches to a previously created cluster.'''
        if vmidefn['vmitype'] == 'vagrant':
            return VagrantVMI(cluster, vmi=vmidefn)
        elif vmidefn['vmitype'] == 'ec2':
            return EC2VMI()

    @abstractmethod
    def jsonmap(self):
        """Returns a JSON-style map representation of the VMI for storage purposes"""

    @abstractmethod
    def start(self):
        """Starts the cluster"""

    @abstractmethod
    def poweron(self, role=None):
        """Power on one or more nodes.  If role=None, then all power on"""

    @abstractmethod
    def poweroff(self, role=None):
        """Power off one or more nodes.  If role=None, then all power off"""

    @abstractmethod
    def pause(self):
        """Pause the cluster (saves state and stops)"""

    @abstractmethod
    def resume(self):
        """Resume the cluster after a pause"""

    @abstractmethod
    def destroy(self):
        """Destroys all file system artifacts related to a cluster.  DESTRUCTIVE operation."""

    @abstractmethod
    def destroy_files_only(self):
        """Destroys local file system artifacts only; useful in cleaning up unit tests.  DESTRUCTIVE operation."""

    @abstractmethod
    def shell_command(self, role, cmd):
        """Runs a shell commnd on the specified cluster node using ssh."""

    @abstractmethod
    def status(self):
        """Reports the aggregate status of the cluster"""
        
    def __init__(self, params):
        '''
        Constructor
        '''
        
