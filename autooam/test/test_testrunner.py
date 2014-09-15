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
Created on Jan 8, 2013

@author: rtw
'''
import unittest
from time import sleep
from autooam.testsuite.testrunner import TestRunner

class TestSuiteStub:
    def __init__(self, wait, ret, withexc=False):
        self._wait = wait
        self._ret = ret
        self._withexc = withexc
    
    def execute(self, cluster, cb=None):
        sleep(self._wait)
        if self._withexc:
            raise Exception('Intentional exception thrown in TestSuiteStub')
        return self._ret

class TestSuiteStepsStub:
    def __init__(self, id):
        self.__id = id
    
    def id(self):
        return self.__id
    
    def execute(self, cluster, cb=None):
        if cb:
            cb('step1')
            cb('step2')
            cb('step3')
        return True

class TestReportStub:
    def __init__(self):
        self.results = []
    
    def new_result(self, suite, result):
        self.results.append((suite, result))
    
class TestRunnerTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBasic(self):
        tr = TestRunner()
        tsstub = TestSuiteStub(1,True)
        result = tr.run(0, tsstub)
        self.assertEqual(result.passfail(), True)
        self.assertAlmostEqual(result.elapsed().total_seconds(), 1.0, 1)


    def testNegative(self):
        tr = TestRunner()
        tsstub = TestSuiteStub(1,False)
        result = tr.run(0, tsstub)
        self.assertEqual(result.passfail(), False)
        self.assertAlmostEqual(result.elapsed().total_seconds(), 1.0, 1)

    
    def testNegativeExc(self):
        tr = TestRunner()
        tsstub = TestSuiteStub(1,True, withexc=True)
        result = tr.run(0, tsstub)
        self.assertEqual(result.passfail(), False)
        self.assertAlmostEqual(result.elapsed().total_seconds(), 1.0, 1)

    def testBasicWithStep(self):
        tr = TestRunner()
        tsstub = TestSuiteStepsStub('unit')
        trstub = TestReportStub()
        result = tr.run(0, tsstub, testreport=trstub)
        self.assertEqual(result.passfail(), True)
        self.assertEqual(len(trstub.results), 3)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
