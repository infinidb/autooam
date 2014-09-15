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
autooam.testmgr.testreport

Class that writes out test report logs
'''

from datetime import datetime
import autooam.common as common
import emtools.common as emcommon
import socket
import pprint
import _mysql
import MySQLdb
import os

class TestReport(object):
    '''
    TestReport writes out test log files
    '''

    def __init__(self, file):
        '''
        Constructor
        
        @param file - output file to write
        '''
        self._file = open(file,'w')
        self._start = datetime.now()
        self._testct = 0
        self._passct = 0
        self._runId = 0
        self._runConfigId = 0
        self._clusterId = 0

        '''
        WWW
        Open MySQL connection and call the start_run stored proc.
        '''
        # TODO: Look into using properties.py for the connection info.
        # TODO: Write the results to the autooam_unit schema instead of autooam when it's a unit test.
        self._mysqlHost = "srvnightly.calpont.com"
        self._mysqlUser = "root"
        if emcommon.props['vmi.vagrantvmi.unit-test']:
                self._mysqlDb = "autooam_unit"
        else:
                self._mysqlDb = "autooam"
        self._conn = MySQLdb.connect(host=self._mysqlHost, user=self._mysqlUser, db=self._mysqlDb)
        cursor = self._conn.cursor ()
        cursor.callproc('start_run',(common.AUTOOAM_VERSION, socket.gethostname(), self._runId))
        # TODO: See if there is a way to grab the runid from the out variable in the stored procedure.
        cursor.execute("SELECT last_insert_id()")
        row = cursor.fetchone ()
        self._runId = row[0]
        cursor.close()
        self._conn.close()

        self._file.write('''


###############################################################################
        Automated Test Report  %s
        autooam version: %s, machine: %s 
###############################################################################
        ''' % (self._start.strftime("%a, %d %b %Y %H:%M:%S"), common.AUTOOAM_VERSION, socket.gethostname()))

    def passing(self):
        return self._passct

    def failing(self):
        return self._testct - self._passct
    
    def total(self):
        return self._testct

    def finish(self):
        elapsed = datetime.now() - self._start
        self._file.write('''

-------------------------------------------------------------------------------
Run Summary:
Elapsed time   : %s
Passing        : %d of %d (%0.1f%%)
''' % (elapsed,
       self._passct,
       self._testct,
       100.0 * self._passct / self._testct ))
        self._file.close()
        
        '''
        WWW
        Close out the run in the MySQL database.
        '''
        self._conn = MySQLdb.connect(host=self._mysqlHost, user=self._mysqlUser, db=self._mysqlDb)
        cursor = self._conn.cursor ()
        # TODO: Determine how to call the stored proc with only one parameter and get rid of the dummy parameter.
        dummy=0
        cursor.callproc('stop_run', (self._runId, dummy))
        cursor.close()
        self._conn.close()

    def email_summary(self, to):
        ''' send a summary email.'''

        if not emcommon.props['vmi.vagrantvmi.unit-test']:
            summfile = '/tmp/run%s' % self._runId
            summ = open(summfile,'w')
            summ.write('''
    Summary Results from: %s
    Passing        : %d of %d (%0.1f%%)
    
    See here for details:
    http://srvnightly.calpont.com/autoOamRunDetails.php?runId=%s&db=autooam
    ''' % (socket.gethostname(),
           self._passct,
           self._testct,
           100.0 * self._passct / self._testct,
           self._runId))
            summ.close()
            
            cmd = 'cat %s | mail -s "autooam results" %s' % (summfile, to)
            os.system(cmd)
        
    def new_config(self, cluster):
        self._file.write('''

-------------------------------------------------------------------------------
        New cluster created at   %s
        
        Cluster Name        : %s
        Cluster ID          : %s
        InfiniDB version    : %s (%s)
        Boxtype             : %s
        Config Name         : %s
        IDB User            : %s
        Data Duplication    : %s
        Binary Installation : %s
        DBRoot Storage Type : %s
        Full config         : %s

-------------------------------------------------------------------------------
''' %       (datetime.now().strftime("%a, %d %b %Y %H:%M:%S"),
             cluster.name(), 
             cluster.id(), 
             cluster.config()['idbversion'], 
             'Ent' if cluster.config()['enterprise'] else 'Std',
             cluster.config()['boxtype'],
             cluster.config()['name'],
             cluster.config()['idbuser'],
             cluster.config()['datdup'],
             cluster.config()['binary'],
             cluster.config()['storage'],
             cluster.jsonmap()))
            
        '''
        WWW
        Add the configuration in the MySQL database.
        '''
        emversion = '' if not cluster.config()['em'] else cluster.config()['em']['version']
        self._conn = MySQLdb.connect(host=self._mysqlHost, user=self._mysqlUser, db=self._mysqlDb)
        cursor = self._conn.cursor ()
        cursor.callproc('start_config', 
                (self._runId, 
                cluster.name(), 
                cluster.id(), 
                '%s (%s)' % (cluster.config()['idbversion'],'Ent' if cluster.config()['enterprise'] else 'Std'), 
                cluster.config()['boxtype'], 
                cluster.config()['name'],
                cluster.config()['idbuser'],
                cluster.config()['datdup'],
                cluster.config()['binary'],
                cluster.config()['storage'],
                cluster.config()['pm_query'],
                emversion))
        # TODO: start_config closes out the prior one, consider instead exposing this in a method here.
        # TODO: See if there is a way to grab the runConfigId from an out parameter.
        sql = "select max(runConfigId) from runConfig where runId=" + str(self._runId) + ";"
        cursor.execute(sql)
        row = cursor.fetchone ()
        self._runConfigId = row[0]
        cursor.close()
        self._conn.close()

    def new_result(self, test, result):
        self._testct += 1
        if result.passfail():
            self._passct += 1
        self._file.write("%-10s%-40s %s   %s\n" % (test.id(),
                                          '%s:' % test.description(),
                                          'Passed' if result.passfail() else 'Failed',
                                          result.elapsed() ) )

        '''
        WWW
        Add the test run result in the MySQL database.
        '''
        self._conn = MySQLdb.connect(host=self._mysqlHost, user=self._mysqlUser, db=self._mysqlDb)
        cursor = self._conn.cursor ()
        cursor.callproc('add_runConfigTest', 
                (self._runId, 
                self._runConfigId,
                test.id(),
                test.description(),
                'Passed' if result.passfail() else 'Failed',
                result.elapsed()))
        cursor.close()
        self._conn.close()
        
        
        
