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
Created on Feb 14, 2013

@author: rtw
'''
import os
import unittest
import emtools.common.utils as utils
import testutils

# simple callback setup to test the debug version of syscall
myret = 0
mydata = ''
mycmd = ''
def mysyscb(cmd):
    global mycmd
    mycmd = cmd
    return (myret, mydata, "")

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testLoggedSyscall(self):
        logfile = "loggedsyscall"
        os.system("rm -f %s" % logfile)
        ret = utils.syscall_log("ls setup.py", logfile)[0]
        self.assertEqual(ret, 0)
        ret = utils.syscall_log("grep notthere setup.py", logfile)[0]
        self.assertEqual(ret, 1)
        ret = utils.syscall_log("cat /etc/foobar", logfile)[0]
        self.assertEqual(ret, 1)

        ref_file = '%s/test1-loggedsyscall' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, logfile))
        # clean up after ourself
        os.system("rm -f %s" % logfile)

    def testNonLoggedSyscall(self):
        (ret, out, outerr) = utils.syscall_log("ls setup.py")
        self.assertEqual(ret, 0)
        self.assertEqual(out, 'setup.py')

    def testDebugLoggedSyscall(self):
        global myret, mydata, mycmd, myscyscb
        utils.syscall_cb = mysyscb

        logfile = "loggedsyscall"
        os.system("rm -f %s" % logfile)

        myret = 0
        mydata = "foo.py\n"
        ret = utils.syscall_log("ls foo.py", logfile)[0]
        self.assertEqual(ret, 0)
        
        myret = 1
        mydata = ""
        ret = utils.syscall_log("grep notthere setup.py", logfile)[0]
        self.assertEqual(ret, 1)
        
        myret = 1
        mydata = "cat: /etc/foodog: No such file or directory\n"
        ret = utils.syscall_log("cat /etc/foodog", logfile)[0]
        self.assertEqual(ret, 1)

        ref_file = '%s/test2-loggedsyscall' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, logfile))
        # clean up after ourself
        os.system("rm -f %s" % logfile)
        
        utils.syscall_cb = None
        
        
    def testDebugNonLoggedSyscall(self):
        global myret, mydata, mycmd, myscyscb
        utils.syscall_cb = mysyscb

        myret = 29
        mydata = "Hello World!"
        (ret,out,outerr) = utils.syscall_log("ls foo.py")
        self.assertEqual(ret, 29)
        self.assertEqual(out, "Hello World!")
        self.assertEqual(mycmd, "ls foo.py")

        utils.syscall_cb = None

    def testSysCallTimeout(self):
        (ret,out,outerr) = utils.syscall_log("find /",timeout=2)
        self.assertEqual(ret, -9)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testLoggedSyscall']
    unittest.main()
