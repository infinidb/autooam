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
autooam.testsuite.testsuite

Arbitrary collection of TestActions.
'''
import os
import time
from datetime import datetime
from abc import ABCMeta, abstractmethod
import emtools.common as common
import emtools.common.logutils as logutils
import json

Log = logutils.getLogger(__name__)

class TestSuite(object):
    '''
    TestSuite is an abstract base class for the actual tests that make up autooam.
    Each test/testsuite subclasses TestSuite and implements the execute() method.
    This class has several helper functions to simplify the syntax for writing 
    tests.
    '''

    def __init__(self, tid, description):
        '''
        Constructor
        '''
        self._id = tid
        self._desc = description
        
    def id(self):
        '''accessor for the TestSuite id.'''
        return self._id
    
    def description(self):
        '''accessor for the TestSuite description.'''
        return self._desc
    
    @abstractmethod
    def execute(self, cluster, cb=None):
        '''Execute the actions on the referenced cluster.'''
        self._cluster = cluster
        self._cb = cb
        self.info_testlog('Starting execution of %s (%s)' % (self._id, self._desc))
        pass
        
    def startstep(self, stepname):
        if self._cb:
            self._cb(stepname)
            
    def info_testlog(self, msg):
        Log.info( msg )
        self.action_system_call('echo "%s"' % msg)
        
    def action_test_script(self, script, role='um1', timeout=0, sleepfor=0, args=''):
        '''
        Run a test script on the cluster under test
        
        @param script     - the script to run, must exist in testsuite.testscript.basedir
        @param role       - optionally specify the role/node to run on (default = um1)
        '''
        scriptsrc = '%s/%s' % (common.props['testsuite.testscript.basedir'], script)
        if not os.path.exists(scriptsrc):
            raise Exception('Test script file %s does not exist!' % self._scriptsrc)
        
        # We rely on the VMI configuration infrastructure to mount /mnt/autooam
        scripttarg = '/mnt/autooam/test-script/%s %s' % (script, args)
        
        return self.action_system_call(scripttarg, role, timeout=timeout, sleepfor=sleepfor)

    def action_system_call(self, cmd, role='pm1', calpontbin=False, successcode=0, timeout=-1, sleepfor=0):
        '''
        Perform a system call on the cluster under test
        
        @param cmd        - the command to run
        @param role       - optionally specify the role/node to run on (default = pm1)
        @param calpontbin - whether the executable is found in Calpont/bin
        @param successcode- optional argument to change which return code is treated as success
        @param timeout    - if non-zero, this is how long the method will retry for a 
                            successful return code.  NOTE - if timeout set, sleepfor most 
                            also be set and vice versa
        @param sleepfor   - if non-zero, this is how long the method sleeps between retries
                            of the command.
        '''
        polling = True if ( timeout>0 and sleepfor>0 ) else False
        shell_timeout = timeout if not polling else -1
        
        if polling:
            Log.info("Will retry command '%s' for %d seconds..." % (cmd, timeout))
        start = datetime.now()
        
        # always guarantee to execute at least once
        ret = self._cluster.shell_command(role, cmd, calpontbin=calpontbin, polling=polling, timeout=shell_timeout)
                
        if polling:
            while (ret != successcode) and (datetime.now() - start).total_seconds() < timeout:
                time.sleep(sleepfor)
                ret = self._cluster.shell_command(role, cmd, calpontbin=calpontbin, polling=polling, timeout=shell_timeout)
            
        if (ret != successcode):
            raise Exception("Test action failure in action_system_call (%s)!" % cmd)

    
    def action_cluster_op(self, op, role=None, minreset=None):
        '''
        Execute the action on the referenced cluster.
        
        @param op       - operation to perform.  One of ('poweroff', 'poweron', 'reset')
        @param role     - optional argument.  If present apply operation on on specified node
        @param minreset - a reset is actually just poweroff followed by poweron.  Because
                          VMs may reset too fast, this parameter is the min. seconds that
                          the node will be down
        '''
        # this will make sure the operation is supported and raise exception if not
        ['poweroff', 'poweron', 'reset'].index(op)            
        
        if op == 'poweroff':
            success = self._cluster.poweroff(role) == 0
        elif op == 'poweron':
            success = self._cluster.poweron(role) == 0
        else:
            ret1 = self._cluster.poweroff(role)
            if minreset:
                time.sleep(minreset)
            ret2 = self._cluster.poweron(role)
            success = ret1 == 0 and ret2 == 0
            
        if not success:
            raise Exception("Test action failure in action_cluster_op (%s)!" % op)
        
    def action_safe_shutdown(self, sleepfor=5):
        '''Execute a shutdown system including a verification check and minimum pause.'''
        
        # do a full shutdown
        self.action_system_call('calpontConsole shutdown y', calpontbin=True)

        # the system always needs a bit of delay after returning from shutdown
        # before we startsystem, reboot or even check that everything is 
        # actually down.
        self.action_system_call('sleep %d' % sleepfor)
        
        # make sure we really shutdown - look for any Calpont processes        
        self.action_test_script('utils/infinidb_not_running.sh',timeout=10,sleepfor=2)
        
    def action_check_cluster_up(self, causeCode='000', timeout=480, role='pm1'):
        if not common.props['cluster.cluster.use_em_for_dbinstall']:
            self.action_system_call('~/healthcheck | grep "<causeCode>%s</causeCode>"' %\
                                    (causeCode), timeout=timeout, sleepfor=5, role=role)
        else:
            self.action_system_call('healthcheck | grep "<causeCode>%s</causeCode>"' %\
                                    (causeCode), timeout=timeout, sleepfor=5, role=role, calpontbin=True)
            
        
    def action_em_checks(self, startTime, query, importTable, importSize, status='ACTIVE', metric='aggregation-cpu-sum.cpu-user' ):
        self.startstep('emStatusCheck')
        self.action_em_status_check('System', status, timeout=60, sleepfor=5)
    
        self.startstep('emMetricsCheck')
        self.action_em_metrics_check(metric)
        
        self.startstep('emQueryCheck')
        self.action_em_query_check(query, startTime)
        
        self.startstep('emImportCheck')
        self.action_em_import_check(importTable, importSize, startTime)
        
        
    def action_em_status_check(self, module, status, timeout=-1, sleepfor=0):
        '''
        Check a module status using the EM REST APIs
        
        @param module     - the module to retrieve status for
        @param status     - the expected status value
        @param timeout    - if non-zero, this is how long the method will retry for a 
                            successful return code.  NOTE - if timeout set, sleepfor most 
                            also be set and vice versa
        @param sleepfor   - if non-zero, this is how long the method sleeps between retries
                            of the command.
        '''
        if common.props['vmi.vagrantvmi.unit-test']:
            return

        polling = True if ( timeout>0 and sleepfor>0 ) else False
        
        if polling:
            Log.info("Will retry command EM status poll for %d seconds..." % (timeout))
        start = datetime.now()
        
        # always guarantee to execute at least once
        if module != 'System':
            modules = self._cluster.emapi().list_modules()
            for m in modules:
                if m['id'] == module:
                    if m['status'] == status:
                        return
        else:
            # for System status we have to retrieve the Clusters instance
            clusterinfo = self._cluster.emapi().get_cluster_info()
            if clusterinfo['status'] == status:
                return
                
        if polling:
            while (datetime.now() - start).total_seconds() < timeout:
                time.sleep(sleepfor)
                if module != 'System':
                    modules = self._cluster.emapi().list_modules()
                    for m in modules:
                        if m['id'] == module:
                            if m['status'] == status:
                                return
                else:
                    # for System status we have to retrieve the Clusters instance
                    clusterinfo = self._cluster.emapi().get_cluster_info()
                    if clusterinfo['status'] == status:
                        return

        # if we get here then we timed out without seeing the status we expect            
        raise Exception("Test action failure in action_em_status_check!")

    def action_em_metrics_check(self, metric, role=None, timeout=120, sleepfor=10):
        '''
        Check a graphite metric using the EM REST APIs
        
        @param metric     - the module to retrieve status for
        @param role       - [optional] defaults to None=all roles
        '''
        if common.props['vmi.vagrantvmi.unit-test']:
            return

        start = int(time.time()) - 60
        
        if role is None:
            roles = self._cluster.machines().keys()
        else:
            roles = [ role ]
            
        for r in roles:
            if r == 'em1':
                # if there is an EM in the cluster we can't get metrics from it
                continue
            
            hostname = self._cluster.machines()[r]['hostname']
            
            startpoll = datetime.now()
            result = self._cluster.emapi().graphite_query(hostname, metric, start)
            while result.find('|') == -1 and (datetime.now() - startpoll).total_seconds() < timeout:
                Log.warning('Invalid return from graphite_query: %s' % result)
                time.sleep(sleepfor)
                result = self._cluster.emapi().graphite_query(hostname, metric, start)
            
            if result.find('|') == -1:
                raise Exception("Test action failure! Invalid graphite query result: %s!" % result)
                
            values = result.split('|')[1]
            found = False
            for v in values.split(','):
                if len(v) and v != 'None':
                    found = True
            
            if not found:
                raise Exception("Test action failure! no non-None values for %s on %s: %s" % (metric, hostname, values))

    def action_em_query_check(self, query, time_min, time_max=None, page_size=25):
        '''
        Check a graphite metric using the EM REST APIs
        
        @param query      - query to search for
        @param time_min   - min time for time window
        @param time_max   - [optional] max time for time window. default = <now>
        @param page_size  - [optional] number of most recent queries to retrieve
        '''
        if common.props['vmi.vagrantvmi.unit-test']:
            return

        if not time_max:
            time_max = time.time()
            
        # adjust min/max to match how queries return time - it is
        # an integer value including milliseconds
        time_min = time_min * 1000
        time_max = time_max * 1000
        
        queries = self._cluster.emapi().get_queries(0, page_size)
        for q in queries:
            if q['startTime'] >= time_min and q['note'] == query and q['endTime'] <= time_max:
                # Success!
                Log.debug('found query match %d milliseconds into range' % (q['startTime'] - time_min))
                return
            
        queries_str = json.dumps(queries, sort_keys=True, indent=4)
        raise Exception("Test action failure! query %s not found for time range %s,%s not found in %s" %\
                         (query, time_min, time_max, queries_str))

    def action_em_import_check(self, table, rows, time_min, time_max=None, page_size=10):
        '''
        Check a graphite metric using the EM REST APIs
        
        @param table      - look for import to this table
        @param rows       - look for an import af this size
        @param time_min   - min time for time window
        @param time_max   - [optional] max time for time window. default = <now>
        @param page_size  - [optional] number of most recent imports to retrieve
        '''
        if common.props['vmi.vagrantvmi.unit-test']:
            return

        if not time_max:
            time_max = time.time()
            
        # adjust min/max to match how queries return time - it is
        # an integer value including milliseconds
        time_min = time_min * 1000
        time_max = time_max * 1000
        
        rowsfound = 0
        imports = self._cluster.emapi().get_loads(0, page_size)
        for i in imports:
            if i['startTime'] >= time_min and i['endTime'] <= time_max:
                try:
                    i['tableList'].index(table)
                    # Success!
                    rowsfound += i['rowsImported']
                except:
                    pass

        if rowsfound == rows:
            Log.debug('found import match %d milliseconds into range' % (i['startTime'] - time_min))
            return
                
        imports_str = json.dumps(imports, sort_keys=True, indent=4)
        raise Exception("Test action failure! import for table %s (%s rows) for time range %s,%s not found in %s" %\
                         (table, rows, time_min, time_max, imports_str))
