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
Created on Jan 15, 2013

@author: rtw
'''
import unittest
import os
import emtools.common as common
import emtools.common.utils as utils
from autooam.vmi.versionmgr import VersionManager
from emtools.cluster.configspec import ConfigSpec
import shutil
import test_common

class Test(unittest.TestCase):


    def setUp(self):
        # use alternate package locations (the alternate locations are
        # set by the test_common import above
        self._pkgpath = common.props['vmi.versionmgr.basedir']
        self._cachepath = common.props['vmi.versionmgr.packagedir']

        # be safe and clear our cache by removing the directory
        if os.path.exists(self._cachepath):
            shutil.rmtree(self._cachepath)

    def tearDown(self):
        # clean up after ourselves
        if os.path.exists(self._cachepath):
            shutil.rmtree(self._cachepath)
        pass
    
    def testBasic(self):        
        
        # standard list_available with no type spec
        v = VersionManager()
        self.assertEqual( sorted(v.list_available()), [ '2.2.11-1', '3.5.1-5', '4.0.0-0' ] )
        
        # standard retrieve from reference with no cache
        pfile = v.retrieve('3.5.1-5','deb')
        self.assertEqual( pfile, '3.5.1-5/packages/calpont-infinidb-ent-3.5.1-5.amd64.deb.tar.gz')
        self.assertEqual( os.path.getmtime('%s/%s' % (self._cachepath, pfile)), 
                          os.path.getmtime('%s/%s' % (self._pkgpath, pfile)))

        # retrieve again - this time should come from cache
        pfile = v.retrieve('3.5.1-5','deb')
        self.assertEqual( pfile, '3.5.1-5/packages/calpont-infinidb-ent-3.5.1-5.amd64.deb.tar.gz')
        self.assertEqual( v.get_pkg_version(pfile), '3.5.1-5' )
        
        # the 'Latest' directory in reference has a bin file
        self.assertEqual( sorted(v.list_available('binary')), [ '2.2.11-1', '3.5.1-5', '4.0', '4.0.0-0', '4.0.0-1', '4.5.0-1', 'Latest' ] )

        with self.assertRaisesRegexp(Exception,"Unsupported package type notype"):
            v.list_available('notype')

        with self.assertRaisesRegexp(Exception,"Unsupported package type newtype"):
            v.retrieve('3.5.1-5','newtype')
            
        # now create something that will be in cache only
        newpath = '%s/Unit-test/packages' % self._cachepath
        utils.mkdir_p(newpath) 
        os.system('touch %s/calpont-infinidb-ent-19.0.1-1.x86_64.rpm.tar.gz' % newpath)
        self.assertEqual( sorted(v.list_available('rpm')), [ '2.2.11-1', '3.5.1-5', '4.0.0-0', 'Unit-test' ] )

        pfile = v.retrieve('Unit-test','rpm')
        self.assertEqual( pfile, '19.0.1-1/packages/calpont-infinidb-ent-19.0.1-1.x86_64.rpm.tar.gz')
        self.assertEqual( v.get_pkg_version(pfile), '19.0.1-1' )
           
        # not try to retrieve some files that don't exist
        with self.assertRaisesRegexp(Exception,"Unable to locate enterprise package for version Unit-test"):
            v.retrieve('Unit-test','deb')

        with self.assertRaisesRegexp(Exception,"Unable to locate enterprise package for version non-existent"):
            v.retrieve('non-existent','deb')

        with self.assertRaisesRegexp(Exception,"Unable to locate enterprise package for version Latest"):
            v.retrieve('Latest','rpm')

        pfile = v.retrieve('Latest','binary')
        self.assertEqual( pfile, '9.9-9/packages/infinidb-ent-9.9-9.x86_64.bin.tar.gz')
        self.assertEqual( v.get_pkg_version(pfile), '9.9-9' )
        refpath = 'Latest/packages/infinidb-ent-9.9-9.x86_64.bin.tar.gz'
        self.assertEqual( os.path.getmtime('%s/%s' % (self._cachepath, pfile)), 
                          os.path.getmtime('%s/%s' % (self._pkgpath, refpath)))
        
        # now we want to force a situation where cached and local copies appear out of sync
        os.system('touch %s/%s' % (self._cachepath, pfile))
        self.assertNotEqual( os.path.getmtime('%s/%s' % (self._cachepath, pfile)), 
                          os.path.getmtime('%s/%s' % (self._pkgpath, refpath)))
        pfile = v.retrieve('Latest','binary')
        self.assertEqual( pfile, '9.9-9/packages/infinidb-ent-9.9-9.x86_64.bin.tar.gz')
        self.assertEqual( os.path.getmtime('%s/%s' % (self._cachepath, pfile)), 
                          os.path.getmtime('%s/%s' % (self._pkgpath, refpath)))

        pfile = v.retrieve('4.0.0-0','binary')
        self.assertEqual( pfile, '4.0.0-0/packages/infinidb-ent-4.0.0-0.x86_64.bin.tar.gz')
        self.assertEqual( os.path.getmtime('%s/%s' % (self._cachepath, pfile)), 
                          os.path.getmtime('%s/%s' % (self._pkgpath, pfile)))
        self.assertEqual( v.get_pkg_version(pfile), '4.0.0-0' )
    
    def testDatdup(self):
                
        # standard list_available with no type spec
        v = VersionManager()
        self.assertEqual( sorted(v.list_available()), [ '2.2.11-1', '3.5.1-5', '4.0.0-0' ] )
        
        # standard retrieve from reference with no cache
        pfile = v.retrieve('3.5.1-5','deb',datdup=True)
        self.assertEqual( pfile, '3.5.1-5/packages/calpont-infinidb-datdup-3.5.1-5.x86_64.bin.tar.gz')
        self.assertEqual( os.path.getmtime('%s/%s' % (self._cachepath, pfile)), 
                          os.path.getmtime('%s/%s' % (self._pkgpath, pfile)))

        pfile = v.retrieve('3.5.1-5','binary',datdup=True)
        self.assertEqual( pfile, '3.5.1-5/packages/calpont-infinidb-datdup-3.5.1-5.x86_64.bin.tar.gz')

        pfile = v.retrieve('3.5.1-5','rpm',datdup=True)
        self.assertEqual( pfile, '3.5.1-5/packages/calpont-datdup-3.5.1-5.x86_64.rpm')

        with self.assertRaisesRegexp(Exception,"Unable to locate datdup package for version 3.5"):
            v.retrieve('3.5','rpm',datdup=True)
    
    def testStd(self):
                
        # standard list_available with no type spec
        v = VersionManager()
        self.assertEqual( sorted(v.list_available()), [ '2.2.11-1', '3.5.1-5', '4.0.0-0' ] )
        
        # standard retrieve from reference with no cache
        pfile = v.retrieve('4.0.0-0','deb',enterprise=False)
        self.assertEqual( pfile, '4.0.0-0/packages/infinidb-4.0.0-0.amd64.deb.tar.gz')
        self.assertEqual( v.get_pkg_version(pfile), '4.0.0-0' )
        self.assertEqual( os.path.getmtime('%s/%s' % (self._cachepath, pfile)), 
                          os.path.getmtime('%s/%s' % (self._pkgpath, pfile)))

        pfile = v.retrieve('4.0.0-0','binary',enterprise=False)
        self.assertEqual( pfile, '4.0.0-0/packages/infinidb-4.0.0-0.x86_64.bin.tar.gz')

        with self.assertRaisesRegexp(Exception,"Unable to locate standard package for version 4.0.0-0, type rpm"):
            v.retrieve('4.0.0-0','rpm',enterprise=False)
    
    def testLatest(self):
        v = VersionManager()
        self.assertEqual( v.latest_release_vers('3.5'), '3.5.1-5' )
        with self.assertRaisesRegexp(Exception,"Latest not in the form of"):
            self.assertEqual( v.latest_release_vers('Latest'), '3.5.1-5' )
        self.assertEqual( v.latest_release_vers('3.5', minusone=True), None )
        
    def testNonStdPkg(self):
        # sometimes we get non-standard package names in the ref area.  Make
        # sure we still handle it
        v = VersionManager()
        versions = sorted(v.list_available('deb'),cmp=ConfigSpec._version_cmp)
        self.assertEqual( versions.count('4.0.0-1_old'), 1 )
    
    def testAutooamUtils(self):
        # sometimes we get non-standard package names in the ref area.  Make
        # sure we still handle it
        v = VersionManager()
        v.retrieve('4.0', 'binary', enterprise = False)
        self.assertTrue( os.path.exists( '%s/%s/packages/Calpont/bin/healthcheck' % (v._cachedir,'4.0-0') ), 
                         '%s/%s/packages/Calpont/bin/healthcheck does not exist' % (v._cachedir,'4.0-0') )
        v.retrieve('Latest', 'binary', enterprise = False)
        self.assertTrue( os.path.exists( '%s/%s/packages/Calpont/bin/healthcheck' % (v._cachedir,'9.9-9') ), 
                         '%s/%s/packages/Calpont/bin/healthcheck does not exist' % (v._cachedir,'9.9-9') )
        v.retrieve('4.0.0-1', 'deb', enterprise = False)
        self.assertTrue( os.path.exists( '%s/%s/packages/Calpont/bin/healthcheck' % (v._cachedir,'4.0.0-1') ), 
                         '%s/%s/packages/Calpont/bin/healthcheck does not exist' % (v._cachedir,'4.0.0-1') )
    
             
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
