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
autooam.vmi.versionmgr

Interact with the existing InfiniDB package area on //calweb/shared
'''
import os
import re
import emtools.common as common
import emtools.common.utils as utils
import emtools.common.logutils as logutils
from emtools.cluster.configspec import ConfigSpec

Log = logutils.getLogger(__name__)

class VersionManager(object):
    '''
    Provide an encapsulation of the InfiniDB package area along with a local
    cache to provide efficient access to InfiniDB software versions at run 
    time.
    
    Unfortunately, this class is way over-complicated at this point due to 
    the vagaries of package handling convention in nightly builds.  Will
    attempt to document this here.
    
    First, there is an inherent difference in the nightly build vs. package 
    build process.
    
    Nightly builds generate a structure in the packages area that looks like 
    this:
        <branch-name | Latest>/packages/infinidb-<pkg version>-...
        
    where:
        <branch-name> is <major>.<minor> - ex. 3.6, 4.0, etc
        Latest - special case for the trunk/develop nightly
        
        <pkg version> is the embedded version in the package.  This will always
        be <major>.<minor>-0, even in the case of 'Latest' (in this case it 
        is numbered according to whatever the next version will be).
        
    Package builds genarate a more consistent structure that looks like:
        <version>/packages/infinidb-<version>-...
    
    In this case, the version number of the subdirectory matches the embedded
    version number in the packages.
    
    The second major gotcha in package handling is packaging differences between
    pre-version 4 packages and version 4 and later packages
    
    Prior to version 4, the only packages built and tested were the enterprise
    packages.  These were prefixed with 'calpont-infinidb'.  Additionally, there
    was a separately packaged 'datdup' package.
    
    After version 4, there are both standard edition and enterprise edition 
    packages, all prefixed with only 'infinidb'.  Further complicating this 
    change is that the autooam framework depends on the healthcheck utility 
    and that is only in the enterprise package.  Hence, when dealing with 
    version 4 or later, there needs to be special handling.  
    '''

    def __init__(self):
        '''
        Constructor.
        
        Ensure that we have a package directory present, then create the
        cache directory if it doesn't already exist.
        '''
        self._basedir = common.props['vmi.versionmgr.basedir']       
        if not os.path.exists(self._basedir):
            raise Exception("Package reference directory %s does not exist!" % self._basedir) 
        self._cachedir = common.props['vmi.versionmgr.packagedir']
        if not os.path.exists(self._cachedir):
            utils.mkdir_p(self._cachedir)
        
        self._filepatt = {
            'binary' : re.compile('(calpont-|)infinidb-ent-([0-9\-\.]*).x86_64.bin.tar.gz'),
            'deb' : re.compile('(calpont-|)infinidb-ent-([0-9\-\.]*).amd64.deb.tar.gz'),
            'rpm' : re.compile('(calpont-|)infinidb-ent-([0-9\-\.]*).x86_64.rpm.tar.gz'),
            'binary-datdup' : re.compile('calpont-infinidb-datdup-(.*).x86_64.bin.tar.gz'),
            # debian support is via the binary package for now
            'deb-datdup' : re.compile('calpont-infinidb-datdup-(.*).x86_64.bin.tar.gz'),
            'rpm-datdup' : re.compile('calpont-datdup-(.*).x86_64.rpm'),
            'binary-std' : re.compile('infinidb-([0-9\-\.]*).x86_64.bin.tar.gz'),
            'deb-std' : re.compile('infinidb-([0-9\-\.]*).amd64.deb.tar.gz'),
            'rpm-std' : re.compile('infinidb-([0-9\-\.]*).x86_64.rpm.tar.gz'),
        }
        self._verspatt = re.compile('(calpont-|)infinidb-(ent-|)(.*).(x86_64.bin|amd64.deb|x86_64.rpm).tar.gz')
        
    def retrieve(self, version, ptype, datdup = False, enterprise = True):
        '''locates the specified version and package type and caches in the local package directory
        
        @param version - version to retrieve.  Must be the name of a directory
                         in the package structure (ex. a directory name under
                         //calweb/shared/Iterations)
        @param ptype   - package type.  One of 'bin', 'deb', or 'rpm'
        @param datdup  - optional argument, if True, retrieves a datdup package. 
                         If False, retrieves the Infinidb main package
        @param enterprise- optional argument, if True, retrieves an enterprise 
                         package.  If False, retrieves a standard edition package
        Returns the relative path to the package tarball which is guaranteed to be
        located in props['vmi.versionmgr.packagedir']
        
        Raises exceptions on failure to locate the specified package (or 
        other misc. errors such as a bad type, etc.).
        '''        
        if not ptype in ['binary', 'deb', 'rpm']:
            raise Exception("Unsupported package type %s!" % ptype)

        # with the introduction of 4.0 standard edition we can't count on healthcheck
        # being present on install.  We will extract out of the binary enterprise 
        # package and make it available for install. this is not an expensive operation 
        # so pull it from the ref area regardless of whether the binary ent package is 
        # cached or not.
        self._get_autooam_utils(version)
            
        ref = self._haspkg(self._basedir, version, ptype, datdup, enterprise)

        altversion = version
        if ref and not datdup and version != self.get_pkg_version(ref[2]):
            # when moving to cache, want to use the real version number
            altversion = self.get_pkg_version(ref[2])

        cache = self._haspkg(self._cachedir, altversion, ptype, datdup, enterprise)
        
        if ref and cache:
            # we found the file in both locations.  need to make sure our cache copy is current
            if os.path.getmtime(ref[0]) != os.path.getmtime(cache[0]):
                # files appear to be different, need to update cache
                return self._update_cache(ref[0], ref[1], ref[2])
            else:
                return '%s/%s' % ( cache[1], cache[2] )
        elif ref:
            # we only found the file in the reference area - copy to local cache
            return self._update_cache(ref[0], ref[1], ref[2])
        elif cache:
            # we only found the file in the cache area - this is not necessarily
            # bad, it just may mean we are running offline or otherwise without
            # access to the package area
            Log.warning("No reference found for %s/%s, using cached copy" % (cache[1], cache[2]))
            return '%s/%s' % ( cache[1], cache[2] )
        else:
            pkg = 'enterprise'
            if datdup:
                pkg = 'datdup'
            elif not enterprise:
                pkg = 'standard'
                
            raise Exception("Unable to locate %s package for version %s, type %s" % (pkg, version, ptype))
        
    def _get_autooam_utils(self, version):
        '''
        Installs required autooam utils that are not packaged in standard 
        edition.  At present, this is only the healthcheck utility, but in 
        the future it may expand to include others.
        
        @param version - version to retrieve.  Must be the name of a directory
                         in the package structure (ex. a directory name under
                         //calweb/shared/Iterations)
        @return        - Boolean value indicating success(True)/failure(False)
                         On failure, an error log of some type will be generated
        '''
        if not version == 'Latest' and version[0] < '4':
            # for versions prior to 4.0 this doesn't make sense - we only
            # test enterprise and it is always in the package
            return True
        binent = self._haspkg(self._basedir, version, 'binary', False, True)
        if not binent:
            Log.error("Unable to extract Calpont/bin/healthcheck for version %s, no binary enterprise package found!" % version)
            return False
        cwd = os.getcwd()
        cachepath = '%s/%s' % (self._cachedir,binent[1]) 
        utils.mkdir_p(cachepath)
        os.chdir(cachepath)
        ret = [ os.system('tar xvzf %s Calpont/bin/healthcheck > /dev/null 2>&1' % binent[0]) >> 8 ]
        if ret[0] != 0:
            Log.error('tar xvzf %s Calpont/bin/healthcheck failed: %s' % (binent[0],ret[0]))
            return False
        
        os.chdir(cwd)
        if not os.path.exists('%s/Calpont/bin/healthcheck' % cachepath):
            Log.error("Unable to extract healthcheck to %s/Calpont/bin/healthcheck" % cachepath)
            return False
        
        return True
    
    def get_pkg_version(self, pfile):
        '''
        Extracts the version number out of a package tarball name.
        
        @param pfile - relative path to a package tarball file
        
        @return      - the version number component that is embedded in 
                       that filename according to the pattern ($1 is the 
                       version number):
            'calpont-infinidb-ent-(.*).(x86_64.bin|amd64.deb|x86_64.rpm).tar.gz'
        
        @raises      - exception if the input file path is malformed.
        '''            
        f = os.path.split(pfile)[1]
        m = self._verspatt.match(f)
        if not m:
            raise Exception("%s does not look like a package file!" % pfile)
        return m.group(3)
    
    def list_available(self, ptype=None):
        '''
        Returns the list of available versions by examining the package areas.
        
        @param ptype - package type to look for.  'bin', 'deb', 'rpm'
        
        @return      - an array containing each valid version for the type 
                       specified.  If no type was specified, it only returns 
                       versions that have all three package types. 
        '''
        
        if ptype and not ptype in ['binary', 'deb', 'rpm']:
            raise Exception("Unsupported package type %s!" % ptype)

        ret = []
        ret.extend(self._listpkgdirs(self._basedir, ptype))
        for i in self._listpkgdirs(self._cachedir, ptype):
            if i not in ret:
                ret.append(i)
        return ret
        
    def latest_release_vers(self, stream, minusone=False):
        '''
        Returns the latest released version from a particular stream.
                
        @param stream   - must be a branch name of the form <major>.<minor>        
        @param minusone - optional Boolean specifying whether it is the last
                          version for the stream or the second to last (i.e.
                          minus one) 
        @return - the last or next to last version on the specified stream or
                  None if no versions for the stream could be located or if
                  minusone is set to True and there is only one version for
                  the stream.
                  
        @raises - exception if an invalid stream is passed in.  
        '''
        
        # The stream must be of the form <major>.<minor>
        if len(stream.split('.')) != 2:
            raise Exception("%s not in the form of <major>.<minor>" % stream)
        
        versions = sorted(self.list_available(),cmp=ConfigSpec._version_cmp)
        lastFromStream = None
        lastMinusOne = None
        for v in versions:
            if v.find(stream) == 0 and v != stream:
                lastMinusOne = lastFromStream
                lastFromStream = v
        return lastFromStream if not minusone else lastMinusOne
        
    def _haspkg(self, loc, version, ptype, datdup, enterprise):
        '''
        Private method that checks a base directory for a particular version and type.

        @param loc      - The base directory to look for package version
                          sub directories.  Specifically, if this method is
                          to return true then <loc> must contain a sub-directory
                          named <version>/packages.
        @param version  - this is the version directory to search for under the
                          <loc> base.  It is not necessarily the version of the
                          packages contained within it if one of the special 
                          nightly build cases described above.
        @param ptype    - must be one of the supported package types - rpm, deb, or
                          binary.
        @param datdup   - boolean indicating whether or not to seach for a datdup
                          package (Note this is only applicable prior to version 4)
        @param enterprise-boolean indicating whether to seach for an enteprise
                          package or a standard package (Note that prior to version
                          4 only enterprise existed)
        @return - None or a 3-tuple consistion of:
                    [0] fully specified path to package,
                    [1] a relative path to where the package would be cached.  Note
                        that the version component of this path will always be the
                        actual version extracted from the package file name.
                    [2] the name of the package file
        '''
        pkgdir = "%s/%s/packages" % (loc, version)
        if not os.path.exists(pkgdir):
            return None
        
        if datdup:
            ptype = "%s-datdup" % ptype
        if not enterprise:
            ptype = "%s-std" % ptype
        for p in os.listdir(pkgdir):
            mat = self._filepatt[ptype].match(p)
            if mat:
                # for version latest we always want to use the real version
                # number when copying to the package cache
                if not datdup:
                    version = self.get_pkg_version(p)
                return ( '%s/%s' % (pkgdir, p), '%s/packages' % version, p )
        return None                
        
    def _update_cache(self, refloc, path, pfile):
        '''
        Private method that updates the cached file of the specified file.
        
        @param refloc   - fully specified path to package.
        @param path     - a relative path to where the package will be cached.
        @param pfile    - name of the package file
        
        Effective the operation is:
            cp -p <refloc> <cache-base>/<path>/.

        @return - relative path of the package file in self._cachedir
        
        @raises - Exception if failed to update cache
        '''
        Log.info('Updating local package cache for %s/%s' % (path,pfile))
        cachepath = self._cachedir + '/' + path
        utils.mkdir_p(cachepath)
        cachefile = cachepath + '/' + pfile
        cmd = 'cp -p %s %s' % (refloc, cachefile)
        ret = os.system(cmd) >> 8
        if ret != 0:
            raise Exception('Failed to copy %s to %s' % (refloc, cachefile))
        return '%s/%s' % (path, pfile)
        
    def _listpkgdirs(self, path, ptype):
        '''
        Private method that iterates through subdirectories in a package area.
        
        @param path     - A path to a directory containing version directories
                          (ex. the calweb Shared Iterations folder)
        @param ptype    - The type of package to check for.  This is passed on
                          to _checkdir below - see more details there.
        
        @return - list of version directories that contain the specified package
                  type.  No sort should be assumed.        
        '''
        if not os.path.exists(path):
            return []
        
        ret = []
        for p in os.listdir(path):
            pdir = '%s/%s' % (path,p)
            if os.path.isdir(pdir) and p != '..' and p != '.':
                if self._checkdir(pdir, ptype):
                    ret.append(p)
        return ret

    def _checkdir(self, path, ptype):
        '''
        Private method that checks a particular directory for existence of 
        packages for the specified type.

        @param path     - A path to a version directory that is assumed to
                          contain packages under a /packages subdirectory
        @param ptype    - The type of package to check for.  It must be one
                          of nine values that are initialized in the constructor.
                          The base must by rpm, deb, or binary and there is 
                          an optional suffix that can be either not present,
                          datdup, or std.
        
        @return - Boolen indicating whether or not the version directory
                  contained the specified package type.
        
        '''
        pkgpath = '%s/packages' % path
        # first check to make sure there is even a packages subdirectory
        if not os.path.exists(pkgpath):
            return False
        
        types = []
        if not ptype:
            types = ['binary', 'deb', 'rpm']
        else:
            types = [ ptype ]
            
        # this isn't particularly efficient, but should never constitute
        # significant runtime
        for t in types:
            found = False
            for p in os.listdir(pkgpath):
                if self._filepatt[t].match(p):
                    found = True
            if not found:
                return False
        return True
