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
autooam.cluster.emvmgr

Contains:
    EMVersiorManager
'''
import os
import re
import glob
import emtools.common as common
import emtools.common.utils as utils
import emtools.common.logutils as logutils
from emtools.cluster.configspec import ConfigSpec

Log = logutils.getLogger(__name__)

class EMVersionManager(object):
    '''
    This class knows how to communicate with the bamboo build area and
    download/cache new packages as necessary.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__packagedir = common.props['cluster.emvmgr.packagedir']
        self.__httpuser = common.props['cluster.emvmgr.httpuser']
        self.__httppassword = common.props['cluster.emvmgr.httppassword']

        self.__pkgmap = {
            'rpm' : 'infinidb-em.rpm',
            'deb' : 'infinidb-em.deb',
            'bin' : 'infinidb-em.tar.gz'
        }
        
        if not os.path.isdir(self.__packagedir):
            utils.mkdir_p(self.__packagedir)

    def retrieve(self, version, ptype):
        '''locates the specified version and package type and caches in the local package directory
        
        @param version - version to retrieve.  Must be the name of a directory
                         in the package structure (ex. a directory name under
                         //calweb/shared/Iterations)
        @param ptype   - package type.  One of 'bin', 'deb', or 'rpm'

        Returns the relative path to the package tarball which is guaranteed to be
        located in props['cluster.emvmgr.basedir']
        
        Raises exceptions on failure to locate the specified package (or 
        other misc. errors such as a bad type, etc.).
        '''        
        # unit test bailout
        if common.props['vmi.vagrantvmi.unit-test']:
            # this is purely made up.  In unit test right now, nobody actually tries to do anything with this return
            return( 'build-99999', os.path.join( common.props['cluster.emvmgr.packagedir'], 'build-99999', 'infinidb-entmgr-1.0-1.el6.x86_64.rpm'))
        
        if version == 'Latest':
            buildver = self._get_current_build_version()
            fname, fsize, fdate = self._get_package_details(ptype)
            Log.info('Current build version is %s' % buildver)
            pkgpath = os.path.join( self.__packagedir, buildver )
            pkgfile = os.path.join( pkgpath, fname )
            if not os.path.isdir( pkgpath ):
                # we don't have this directory at all so we know we will create and download
                utils.mkdir_p( pkgpath )
            else:
                # the directory already exists - let's see if the file is already current
                if os.path.exists(pkgfile) and eval(fsize) == os.path.getsize(pkgfile):
                    Log.info('Package %s is already up-to-date' % pkgfile)
                    return (buildver, pkgfile)
            
            Log.info('Fetching %s into %s' % (fname, pkgpath))
            
            cmd = 'wget -O %s --http-user=%s --http-password=%s https://infinidb.atlassian.net/builds/artifact/EM-EM/shared/build-latest/%s/%s?os_authType=basic' %\
                ( pkgfile, self.__httpuser, self.__httppassword, self.__pkgmap[ptype], fname )
            
            rc, out, err = utils.syscall_log(cmd)

            return (buildver, pkgfile)
        else:
            # in this case we aren't going to contact the bamboo server, but 
            # rather use a previously downloaded version
            pkgpath = os.path.join( self.__packagedir, version )
            if not os.path.isdir( pkgpath ):
                Log.error('Error retrieving EM version %s, %s path does not exist' % (version, pkgpath))
                return (None, None)
            
            fileext = ptype if ptype != 'bin' else '.tar.gz'
            pkgs = glob.glob('%s/*%s' % (pkgpath, fileext))
            if len(pkgs) == 0:
                Log.error('No packages of type %s found in %s' % (ptype, pkgpath))
                return (None, None)
            else:
                if len(pkgs) > 1:
                    Log.warn('Multiple packages of type %s found in %s, using first : %s' % (ptype, pkgpath, pkgs))
                return (version, pkgs[0])
        
    def _get_current_build_version(self):
        cmd = 'wget -qO- --http-user=%s --http-password=%s https://infinidb.atlassian.net/builds/artifact/EM-EM/shared/build-latest/?os_authType=basic' %\
                ( self.__httpuser, self.__httppassword )
                
        rc, out, err = utils.syscall_log(cmd)
        if rc != 0:
            Log.error('Failed to retrieve current build version.  Command %s return %s:%s' % (cmd, rc, out))
            return None
        
        bldidpatt = re.compile('.*(build-[0-9]+).*')
        mat = bldidpatt.match(out)
        if mat:
            return mat.group(1)
        else:
            Log.error('Retrieve of build-latest folder does not appear to contain a build number: %s' % out)
            return None
        
    def _get_package_details(self, ptype):

        cmd = 'wget -qO- --http-user=%s --http-password=%s https://infinidb.atlassian.net/builds/artifact/EM-EM/shared/build-latest/%s?os_authType=basic' %\
                ( self.__httpuser, self.__httppassword, self.__pkgmap[ptype] )
                
        rc, out, err = utils.syscall_log(cmd)
        if rc != 0:
            Log.error('Failed to retrieve package details.  Command %s return %s:%s' % (cmd, rc, out))
            return None

        # regex won't work across newlines so we strip them out        
        out = out.replace('\n','')
        # split based on HTTP table cells
        cells = out.split('</TD>')
        # now fields should be as follows:
        #   [0] - file name
        #   [1] - file size
        #   [2] - file datetime
        filepatt = re.compile('.*>(infinidb-.*)</a>.*')
        sizepatt = re.compile('.*>([0-9]+) bytes.*')
        datepatt = re.compile('<TD>(.*)')

        filemat = filepatt.match(cells[0])
        sizemat = sizepatt.match(cells[1])
        datemat = datepatt.match(cells[2])
        if filemat:
            fname = filemat.group(1)
        else:
            Log.error('Retrieve of %s package does not appear to contain a filename: %s' % (ptype, cells[0]) )
            return None
        if sizemat:
            fsize = sizemat.group(1)
        else:
            Log.error('Retrieve of %s package does not appear to contain a file size: %s' % (ptype, cells[1]) )
            return None
        if datemat:
            fdate = datemat.group(1)
        else:
            Log.error('Retrieve of %s package does not appear to contain a date: %s' % (ptype, cells[2]) )
            return None
        
        return fname, fsize, fdate
