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
autooam.testlib.tests

module test factory methods
'''
import sys,inspect
from autooam.testsuite.testsuite import TestSuite
import time

class basic001(TestSuite):
    '''run a simple smoke test on a cluster.'''
    def __init__(self):
        TestSuite.__init__(self,'basic001','a simple smoke test')
        
    def execute(self, cluster, cb=None):
        TestSuite.execute(self, cluster, cb=cb)
        
        start = time.time()

        self.startstep('dbFunctional')
        self.action_test_script('basic/dbFunctional.sh', timeout=600)
        
        if cluster.emapi():
            self.action_em_checks(start, 'select count(*) from dbFunctional', 'dbFunctional.dbFunctional', 160000)

        return True
        
class basic002(TestSuite):
    '''simple test with various shutdown, start, stop, restart, etc. commands.'''
    def __init__(self):
        TestSuite.__init__(self,'basic002','simple test with oam commands')
        
    def __verify_em(self, start):      
        if self._cluster.emapi():  
            self.action_em_checks(start, 'select count(*) from loads', 'dbFunctional.t1', 100000)
        
    def execute(self, cluster, cb=None):
        TestSuite.execute(self, cluster, cb=cb)

        # check functionality
        start = time.time()
        self.startstep('upgradeTest2')
        self.action_test_script('upgrade/upgradeTest2.sh', args='new', timeout=600)

        self.__verify_em(start)
        
        # shutdown infinidb
        self.startstep('shutdown')
        self.action_safe_shutdown()
        
        # start infinidb 
        self.startstep('startsystem')
        self.action_system_call('calpontConsole startsystem', calpontbin=True)
                
        # a little time to really finish        
        self.action_system_call('sleep 5')

        # check functionality
        start = time.time()
        self.startstep('upgradeTest2')
        self.action_test_script('upgrade/upgradeTest2.sh', args='upgrade', timeout=600)
        self.__verify_em(start)

        # infinidb restart 
        self.startstep('restartsystem')
        self.action_system_call('calpontConsole restartsystem y', calpontbin=True)

        # a little time to really finish        
        self.action_system_call('sleep 5')        

        # check functionality
        start = time.time()
        self.startstep('upgradeTest2')
        self.action_test_script('upgrade/upgradeTest2.sh', args='upgrade', timeout=600)
        self.__verify_em(start)

        # infinidb stop 
        self.startstep('stopsystem')
        self.action_system_call('calpontConsole stopsystem y', calpontbin=True)

        # a little time to really finish
        self.action_system_call('sleep 5')

        # start the system 
        self.startstep('startsystem')
        self.action_system_call('calpontConsole startsystem', calpontbin=True)
                
        # a little time to really finish        
        self.action_system_call('sleep 5')        

        # check functionality
        start = time.time()
        self.startstep('upgradeTest2')
        self.action_test_script('upgrade/upgradeTest2.sh', args='upgrade', timeout=600)
        self.__verify_em(start)

        # shutdown infinidb
        self.action_safe_shutdown()

        # reset the cluster
        self.startstep('power-on reset')
        self.action_cluster_op('reset', minreset=5)
        
        # have to wait for the cluster to recover.
        self.startstep('healthCheck')
        self.action_check_cluster_up()
        
        # check functionality
        start = time.time()
        self.startstep('upgradeTest2')
        self.action_test_script('upgrade/upgradeTest2.sh', args='upgrade', timeout=600)
        self.__verify_em(start)
        return True    
    
class upgrade001(TestSuite):
    '''Some basic 1G tpch testing before and after an upgrade.'''
    def __init__(self):
        TestSuite.__init__(self,'upgrade001','Some basic testing before and after an upgrade')
        
    def __verify_em(self, start):      
        if self._cluster.emapi():  
            self.action_em_checks(start, 'select count(*) from loads', 'dbFunctional.t1', 100000)

    def execute(self, cluster, cb=None):
        TestSuite.execute(self, cluster, cb=cb)
                
        # check functionality
        start = time.time()
        self.startstep('upgradeTest2')
        self.action_test_script('upgrade/upgradeTest2.sh', args='new', timeout=600)
        self.__verify_em(start)

        # upgrade if config specified one
        if cluster.config()['upgrade']:
            # shutdown infinidb
            self.startstep('shutdownsystem')
            self.action_safe_shutdown()

            # if successful, this will leave the cluster running
            self.startstep('run_upgrade_recipe')
            cluster.run_upgrade_recipe()

            # check functionality
            start = time.time()
            self.startstep('upgradeTest2')
            self.action_test_script('upgrade/upgradeTest2.sh', args='upgrade', timeout=600)
            self.__verify_em(start)
            
        return True    

class moduleFailover(TestSuite):
    '''Module failover test, validate functionality before, during, after.'''
    def __init__(self, testpm1_fail = True):
        TestSuite.__init__(self,'moduleFailover','Module Failover Test')
        self._testpm1_fail = testpm1_fail

    def __verify_em(self, start):      
        if self._cluster.emapi():  
            self.action_em_checks(start, 'select count(*) from loads', 'dbFunctional.t1', 100000)
        
    def execute(self, cluster, cb=None):
        TestSuite.execute(self, cluster, cb=cb)

        pmCount = cluster.config().total_pm_count()

        if pmCount < 2:
                raise Exception('Module Failover only for Multi-Node System')

        umCount = cluster.config().total_um_count()        
        if umCount > 0:
                testRole='um1'
        else:
                testRole='pm1'

        # a little time to really finish
        self.action_system_call('sleep 10')

        # check functionality
        start = time.time()
        self.startstep('upgradeTest2')
        self.action_test_script('upgrade/upgradeTest2.sh', args='new', timeout=600)
        self.__verify_em(start)
   
        moduleid=pmCount
        lastid = 0 if self._testpm1_fail else 1
        while (moduleid > lastid):
            activePM='pm1'

            failoverPM='pm'+str(moduleid)
           
            if activePM == failoverPM:
                activePM='pm2'

            if testRole != 'um1':
                testRole=activePM

            # power off pm
            self.startstep('poweroff %s' % failoverPM)
            self.action_cluster_op('poweroff', role=failoverPM)
                    
            # a little time to really finish
            self.action_system_call('sleep 60', role=activePM)
            
            # have to wait for the cluster to get functional.
            self.startstep('check failover')
            self.action_check_cluster_up( causeCode='101', role=activePM)
     
            # a little time to really finish
            self.action_system_call('sleep 10', role=activePM)
    
            # check functionality
            start = time.time()
            self.startstep('upgradeTest2')
            self.action_test_script('upgrade/upgradeTest2.sh', args='upgrade', timeout=600)
            self.__verify_em(start)
    
            # power on pm
            self.startstep('poweron %s' % failoverPM)
            self.action_cluster_op('poweron', role=failoverPM)
                    
            # have to wait for the cluster to recover.
            self.startstep('check recover')
            self.action_check_cluster_up( causeCode='000', role=activePM)
            
            # a little time to really finish
            self.action_system_call('sleep 10', role=activePM)
    
            # check functionality
            start = time.time()
            self.startstep('upgradeTest2')
            self.action_test_script('upgrade/upgradeTest2.sh', args='upgrade', timeout=600)
            self.__verify_em(start)
            
            moduleid=moduleid-1
        
        # switch active pm back to pm1 
        self.startstep('calpontConsole switchparentoammodule pm1')
        self.action_system_call('calpontConsole switchparentoammodule pm1 y', calpontbin=True)
        
        # a little time to really finish
        self.action_system_call('sleep 10')
    
        # check functionality
        start = time.time()
        self.startstep('upgradeTest2')
        self.action_test_script('upgrade/upgradeTest2.sh', args='upgrade', timeout=600)
        self.__verify_em(start)

        return True    

def list_all():
    register = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and name != 'TestSuite':
            register.append((name,obj.__doc__, obj))
    return register

def call_by_name(name):
    thismodule = sys.modules[__name__]
    fn = getattr(thismodule,name)
    return fn()
