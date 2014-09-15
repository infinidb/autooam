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
Created on May 7, 2014

@author: bwilkinson
'''
import unittest
import emtools.common.utils as utils
import test_common
import autooam.cluster.emvmgr as emvmgr
import emtools.common as common
import os
import shutil
import time

# callbacks to test various wget paths
def mysyscb1(cmd):
    ret = '''<HTML><HEAD><TITLE>build-00162</TITLE></HEAD><BODY>
<H1>build-00162</H1><TABLE BORDER=0><TR><TD><A HREF=../shared>Parent Directory</A></TD><TD></TD><TD></TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.deb">infinidb-em.deb</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:26 AM</TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.rpm">infinidb-em.rpm</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:33 AM</TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.tar.gz">infinidb-em.tar.gz</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:40 AM</TD></TR>
</TABLE>
'''
    return (0, ret, '')

def mysyscb2(cmd):
    ret = '''<HTML><HEAD><TITLE>infinidb-em.rpm</TITLE></HEAD><BODY>
<H1>infinidb-em.rpm</H1><TABLE BORDER=0><TR><TD><img src="/builds/images/icons/icon_file.gif" alt="(file)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.rpm/infinidb-entmgr-1.0-11.el6.x86_64.rpm">infinidb-entmgr-1.0-11.el6.x86_64.rpm</a>&nbsp;</TD><TD ALIGN=right>999 bytes&nbsp;</TD><TD>May 6, 2014 12:50:33 AM</TD></TR>
</TABLE>
'''
    return (0, ret, '')

def mysyscb3(cmd):
    ret = '''<HTML><HEAD><TITLE>infinidb-em.tar.gz</TITLE></HEAD><BODY>
<H1>infinidb-em.tar.gz</H1><TABLE BORDER=0><TR><TD><img src="/builds/images/icons/icon_file.gif" alt="(file)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.tar.gz/infinidb-em-1.0.0.tar.gz">infinidb-em-1.0.0.tar.gz</a>&nbsp;</TD><TD ALIGN=right>1111 bytes&nbsp;</TD><TD>May 6, 2014 12:50:40 AM</TD></TR>
</TABLE>
'''
    return (0, ret, '')

def mysyscb4(cmd):
    ret = '''HTML><HEAD><TITLE>infinidb-em.deb</TITLE></HEAD><BODY>
<H1>infinidb-em.deb</H1><TABLE BORDER=0><TR><TD><img src="/builds/images/icons/icon_file.gif" alt="(file)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.deb/infinidb-entmgr-1.0-11.el6.x86_64.deb">infinidb-entmgr-1.0-11.el6.x86_64.deb</a>&nbsp;</TD><TD ALIGN=right>1212 bytes&nbsp;</TD><TD>May 6, 2014 12:50:33 AM</TD></TR>
</TABLE>
'''
    return (0, ret, '')

# going to simulate a retrieve
cb5_idx = 0
cb5_rets = [
    '''<HTML><HEAD><TITLE>build-00162</TITLE></HEAD><BODY>
<H1>build-00162</H1><TABLE BORDER=0><TR><TD><A HREF=../shared>Parent Directory</A></TD><TD></TD><TD></TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.deb">infinidb-em.deb</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:26 AM</TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.rpm">infinidb-em.rpm</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:33 AM</TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.tar.gz">infinidb-em.tar.gz</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:40 AM</TD></TR>
</TABLE>''',
    '''<HTML><HEAD><TITLE>infinidb-em.tar.gz</TITLE></HEAD><BODY>
<H1>infinidb-em.tar.gz</H1><TABLE BORDER=0><TR><TD><img src="/builds/images/icons/icon_file.gif" alt="(file)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.tar.gz/infinidb-em-1.0.0.tar.gz">infinidb-em-1.0.0.tar.gz</a>&nbsp;</TD><TD ALIGN=right>15 bytes&nbsp;</TD><TD>May 6, 2014 12:50:40 AM</TD></TR>
</TABLE>''',
    '' # this is the cmd to fetch the package
]
def mysyscb5(cmd):
    global cb5_idx, cb5_rets
    cb5_idx = cb5_idx + 1
    if cb5_idx == 3:
        f = open( os.path.join( common.props['cluster.emvmgr.packagedir'], 'build-00162', 'infinidb-em-1.0.0.tar.gz' ), 'w' )
        f.write('hello unit test')
        f.close()
    return (0, cb5_rets[cb5_idx-1], '')

cb6_idx = 0
cb6_rets = [
    '''<HTML><HEAD><TITLE>build-00162</TITLE></HEAD><BODY>
<H1>build-00162</H1><TABLE BORDER=0><TR><TD><A HREF=../shared>Parent Directory</A></TD><TD></TD><TD></TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.deb">infinidb-em.deb</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:26 AM</TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.rpm">infinidb-em.rpm</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:33 AM</TD></TR>
<TR><TD><img src="/builds/images/icons/icon_folder.gif" alt="(dir)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.tar.gz">infinidb-em.tar.gz</a>&nbsp;</TD><TD ALIGN=right>4096 bytes&nbsp;</TD><TD>May 6, 2014 12:50:40 AM</TD></TR>
</TABLE>''',
    '''<HTML><HEAD><TITLE>infinidb-em.tar.gz</TITLE></HEAD><BODY>
<H1>infinidb-em.tar.gz</H1><TABLE BORDER=0><TR><TD><img src="/builds/images/icons/icon_file.gif" alt="(file)">&nbsp;<A HREF="/builds/artifact/EM-EM/shared/build-latest/infinidb-em.tar.gz/infinidb-em-1.0.0.tar.gz">infinidb-em-1.0.0.tar.gz</a>&nbsp;</TD><TD ALIGN=right>19 bytes&nbsp;</TD><TD>May 6, 2014 12:50:40 AM</TD></TR>
</TABLE>''',
    '' # this is the cmd to fetch the package
]
def mysyscb6(cmd):
    global cb6_idx, cb6_rets
    cb6_idx = cb6_idx + 1
    if cb6_idx == 3:
        f = open( os.path.join( common.props['cluster.emvmgr.packagedir'], 'build-00162', 'infinidb-em-1.0.0.tar.gz' ), 'w' )
        f.write('hello unit test 2')
        f.close()
    return (0, cb6_rets[cb6_idx-1], '')

class EMVmgrTest(unittest.TestCase):


    def setUp(self):
        self.__packagedirsave = common.props['cluster.emvmgr.packagedir']
        common.props['cluster.emvmgr.packagedir'] = '%s/pkg-em' % os.path.dirname(__file__)
        # for this particular test we actually want this off because we simulate responsese with above code
        common.props['vmi.vagrantvmi.unit-test'] = False
        shutil.rmtree(common.props['cluster.emvmgr.packagedir'],ignore_errors=True)

    def tearDown(self):
        utils.syscall_cb = None
        shutil.rmtree(common.props['cluster.emvmgr.packagedir'],ignore_errors=True)
        common.props['vmi.vagrantvmi.unit-test'] = True
        common.props['cluster.emvmgr.packagedir'] = self.__packagedirsave

    def testBuildVersion(self):
        utils.syscall_cb = mysyscb1
        e = emvmgr.EMVersionManager()
        self.assertEquals(e._get_current_build_version(), 'build-00162')

    def testPackageDetails(self):
        utils.syscall_cb = mysyscb2
        e = emvmgr.EMVersionManager()
        fname, fsize, fdate = e._get_package_details('rpm')
        self.assertEquals(fname, 'infinidb-entmgr-1.0-11.el6.x86_64.rpm')
        self.assertEquals(fsize, '999')
        self.assertEquals(fdate, 'May 6, 2014 12:50:33 AM')
        
        utils.syscall_cb = mysyscb3
        fname, fsize, fdate = e._get_package_details('bin')
        self.assertEquals(fname, 'infinidb-em-1.0.0.tar.gz')
        self.assertEquals(fsize, '1111')
        self.assertEquals(fdate, 'May 6, 2014 12:50:40 AM')

        utils.syscall_cb = mysyscb4
        fname, fsize, fdate = e._get_package_details('deb')
        self.assertEquals(fname, 'infinidb-entmgr-1.0-11.el6.x86_64.deb')
        self.assertEquals(fsize, '1212')
        self.assertEquals(fdate, 'May 6, 2014 12:50:33 AM')

    def testRetrieve(self):
        utils.syscall_cb = mysyscb5
        e = emvmgr.EMVersionManager()
        (ver, pkg) = e.retrieve('Latest','bin')
        self.assertEquals(pkg, '%s/pkg-em/build-00162/infinidb-em-1.0.0.tar.gz' % os.path.dirname(__file__))
        self.assertEqual(ver, "build-00162")
        
        mtime1 = os.path.getmtime('autooam/test/pkg-em/build-00162/infinidb-em-1.0.0.tar.gz')
        # make sure we would get a different time if it reissued the wget download
        time.sleep(1)
        
        # reset our syscall above
        global cb5_idx
        cb5_idx = 0
        
        (ver, pkg) = e.retrieve('Latest','bin')
        mtime2 = os.path.getmtime('%s/pkg-em/build-00162/infinidb-em-1.0.0.tar.gz' % os.path.dirname(__file__))
        self.assertEqual(mtime1, mtime2)

        utils.syscall_cb = mysyscb6
        (ver, pkg) = e.retrieve('Latest','bin')
        self.assertEquals(pkg, '%s/pkg-em/build-00162/infinidb-em-1.0.0.tar.gz' % os.path.dirname(__file__))
        mtime2 = os.path.getmtime('autooam/test/pkg-em/build-00162/infinidb-em-1.0.0.tar.gz')
        self.assertNotEqual(mtime1, mtime2)

        (ver, pkg) = e.retrieve('build-00162','bin')
        self.assertEqual(ver, "build-00162")
        self.assertEquals(pkg, '%s/pkg-em/build-00162/infinidb-em-1.0.0.tar.gz' % os.path.dirname(__file__))
        (ver, pkg) = e.retrieve('build-99999','bin')
        self.assertEquals(pkg, None)
        self.assertEqual(ver, None)
        (ver, pkg) = e.retrieve('build-00162','rpm')
        self.assertEquals(pkg, None)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()