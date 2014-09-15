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
Created on Feb 22, 2013

@author: rtw
'''
import unittest
import os
import emtools.common.utils as utils

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBasic1(self):
        '''Test launchcluster and various clustercmd's against a multi node cluster.'''
        (ret, output, outerr) = utils.syscall_log('%s/bin/launchcluster.py -u unittest multi_1um_2pm cal-precise64 3.5.1-5' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u poweroff unittest' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u poweron unittest' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u pause unittest' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u resume unittest' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u show unittest' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u run unittest basic001' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u destroy unittest' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        pass

    def testBasic2(self):
        '''Test launchcluster -f operation.'''
        (ret, output, outerr) = utils.syscall_log('%s/bin/launchcluster.py -u -f unittest-b2 %s/examples/single.json cal-precise64 3.5.1-5' % (os.environ['AUTOOAM_HOME'],os.environ['AUTOOAM_HOME']))
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u destroy unittest-b2' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        pass

    def testBasic3(self):
        '''Test launchcluster and various clustercmd's against a single node cluster.'''
        (ret, output, outerr) = utils.syscall_log('%s/bin/launchcluster.py -u unittest-b3 singlenode cal-precise64 3.5.1-5' % (os.environ['AUTOOAM_HOME']))
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u poweroff unittest-b3' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u poweron unittest-b3' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u show unittest-b3' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u run unittest-b3 basic001' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        (ret, output, outerr) = utils.syscall_log('%s/bin/clustercmd.py -u destroy unittest-b3' % os.environ['AUTOOAM_HOME'])
        self.assertEqual(ret,0,output)
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
