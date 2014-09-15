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
autooam.testmgr.testmgr

Coordinator class that knows how to create clusters and run tests
'''

import os,sys
import time
from autooam.cluster.clustermgr import ClusterMgr
from autooam.testsuite.testrunner import TestRunner
from testreport import TestReport
from datetime import datetime
from autooam.testsuite.testresult import TestResult
from autooam.testsuite.testsuite import TestSuite
from emtools.common.utils import syscall_log
import emtools.common as common

import emtools.common.logutils as logutils
Log = logutils.getLogger(__name__)

class TestManager(object):
    '''
    TestManager provides the run_all() method for overall coordination of 
    running a group of cluster config/test requests
    '''

    def __init__(self, log):
        '''
        Constructor
        '''
        self._log = log
        self._testreport = TestReport(self._log)
        self._startupsuite = TestSuite('startup', 'cluster install and startup')
        self._installsuite = TestSuite('install', 'InfiniDB installation')
        self.__current_step = None
        
    def test_report(self):
        return self._testreport
        
    def run_all(self, runlist):
        '''
        Run each test on the runlist.
        
        @param runlist - container of tuples of the form 
                             (ConfigSpec,vmi-type,TestSuite)        
        '''
        mgr = ClusterMgr()
        tr = TestRunner()
        
        last_config = ''
        cluster = 0
        overall = True
        cluster_failed = False
        
        for t in runlist:
            cfgspec, vmitype, testsuite = t
            
            # always allocate new cluster
            if True:
                # the config is new
                if cluster:
                    if not cluster_failed or common.props['vmi.vagrantvmi.unit-test']:
                        Log.info("Cleaning up passed cluster %s" % cluster.name())
                        mgr.destroy(cluster)
                    else:                    
                        Log.info("Pausing failed cluster %s" % cluster.name())
                        if common.props['testmgr.testmgr.pause_failed']:
                            cluster.pause()
                        # TODO - this is a workaround that we need right now because
                        # the behavior of one cluster in the EM can affect all others.
                        # For now we detach from the EM for any failed cluster.  It
                        # can always be re-attached later.
                        if cluster.emapi():
                            cluster.emapi().delete()
      
                cluster_failed = False
                last_config = cfgspec.json_dumps()
                
                name = 'test-mgr%0.0f' % time.time()
                Log.info("Allocating new cluster %s" % name)
                #dmc control chef vs ansible mode through chefmode flag
                cluster = mgr.alloc_new(name,cfgspec,vmitype,chefmode=False)
                self._testreport.new_config(cluster)

                # we are going to treat cluster startup as a special testcase 0
                cstart = datetime.now() 
                try:
                    cluster_failed = cluster.start() != 0
                except:
                    # if start() throws an exception the error is serious enough that 
                    # we want to abort execution
                    Log.fatal('Test run aborted')
                    return False
                
                if cluster_failed:
                    overall = False
                cstart_res = TestResult(cstart, datetime.now(), not cluster_failed)
                self._testreport.new_result(self._startupsuite, cstart_res)
                
                if not cluster_failed:
                    # vms are up - try to install
                    istart = datetime.now()
                    #cluster_failed = cluster.run_install_recipe(cb = None) != 0
                    cluster_failed = cluster.run_install_recipe(cb = self.startinstallstep_cb) != 0
                    # if the install is registering steps, handle the last one
                    if self.__current_step:
                        res = TestResult(self.__current_start, datetime.now(), not cluster_failed)
                        self._testreport.new_result(self.__current_step, res)
                        self.__current_step = None       
                                    
            if not cluster_failed:
                Log.info("Running test %s" % testsuite.id())
                result = tr.run(cluster, testsuite, testreport=self._testreport)

                if not result.passfail():
                    overall = False
                    cluster_failed = True
                
        if cluster:
            if not cluster_failed or common.props['vmi.vagrantvmi.unit-test']:
                Log.info("Cleaning up passed cluster %s" % cluster.name())
                mgr.destroy(cluster)
            else:                    
                Log.info("Pausing failed cluster %s" % cluster.name())
                if common.props['testmgr.testmgr.pause_failed']:
                    cluster.pause()
                # TODO - this is a workaround that we need right now because
                # the behavior of one cluster in the EM can affect all others.
                # For now we detach from the EM for any failed cluster.  It
                # can always be re-attached later.
                if cluster.emapi():
                    cluster.emapi().delete()
        
        self._testreport.finish()
        
        self._testreport.email_summary(common.props['testmgr.testmgr.emaildist'])
        
        return overall
        
    def startinstallstep_cb(self, stepname):
        if not self._testreport:
            return
        
        if self.__current_step:
            # we are starting a new step so the previous must have passed
            res = TestResult(self.__current_start, datetime.now(), True)
            self._testreport.new_result(self.__current_step, res)       
                         
        self.__current_start = datetime.now()
        self.__current_step = TestSuite(self._installsuite.id(), stepname)

