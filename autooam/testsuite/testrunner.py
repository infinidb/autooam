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
autooam.testscript.testrunner

A TestRunner is capable of executing a TestScript against a cluster and 
making the corresponding TestResult instances available as results
'''
from datetime import datetime
from testresult import TestResult
import time
from datetime import datetime
from autooam.testsuite.testsuite import TestSuite

import emtools.common.logutils as logutils
Log = logutils.getLogger(__name__)

class TestRunner(object):
    '''
    TestRunner exists to provide the run() method below.  It's debatable
    on whether this should be a class at all.  It could be as simple as
    just the one method.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.__current_step = None
        
    def run(self, cluster, testsuite, testreport=None):     
        '''runs the testsuite against the cluster and returns a TestResult instance.'''
        self.__testreport = testreport
        self.__testsuite = testsuite
        start = datetime.now()    
        try:    
            ret = testsuite.execute(cluster, cb=self.startstep_cb)
        except Exception as exc:
            Log.error('Test execution failure: %s' % exc)
            if self.__current_step and self.__testreport:
                # if this is set it means that this is the step that failed.  We will report as such
                res = TestResult(self.__current_start, datetime.now(), False)
                self.__testreport.new_result(self.__current_step, res)
                self.__current_step = None
            ret = False
                    
        end = datetime.now()
        # if we get here then the last step passed
        if self.__current_step and self.__testreport:
            res = TestResult(self.__current_start, datetime.now(), True)
            self.__testreport.new_result(self.__current_step, res)
            self.__current_step = None

        return TestResult(start, end, ret)
        
    def startstep_cb(self, stepname):
        if not self.__testreport:
            return
        
        if self.__current_step:
            # we are starting a new step so the previous must have passed
            res = TestResult(self.__current_start, datetime.now(), True)
            self.__testreport.new_result(self.__current_step, res)       
                         
        self.__current_start = datetime.now()
        self.__current_step = TestSuite(self.__testsuite.id(), stepname)
            