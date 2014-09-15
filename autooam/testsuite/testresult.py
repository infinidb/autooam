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
autooam.testsuite.testresult

TestResult instances represent the results of a TestAction that has been 
executed on a cluster
'''

class TestResult(object):
    '''
    Simple struct-like container for results of a test run.
    '''

    def __init__(self, start, end, passfail):
        '''
        Constructor
        
        @param start    - datetime when execution started
        @param end      - datetime when execution finished
        @param passfail - boolean indicating success/failure
        '''
        self._start = start
        self._end = end
        self._passfail = passfail
        
    def start(self):
        '''Accessor for the start time.'''
        return self._start
    
    def elapsed(self):
        '''Returns elapsed test time as a timedelta object.'''
        return self._end - self._start
    
    def passfail(self):
        '''Accessor for the passfail member.'''
        return self._passfail
        