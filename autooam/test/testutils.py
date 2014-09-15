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
autooam.test.testutils

Utility methods for the unit test infrastructure
'''

import os
import re
import emtools.common.logutils as logutils
import socket
import autooam.common as common

Log = logutils.getLogger(__name__)

def file_compare(file1, file2):
    """Compares the two files with handling for variable substitution,
    wildcarding, and truncation versus the reference file.
    
    @param file1 - the reference file with potential variables to be substituted
    @param file2 - target file
    
    Variables following an environment style syntax ($VARIABLE) listed in
    the subs array are substituted.
    
    Any * character found in the reference file is transferred over to the
    target before comparison
    
    If a ^ is present in the reference file, the target is truncated at that
    point prior to comparison
    """    
    subs = [('\$AUTOOAM_HOME', os.environ['AUTOOAM_HOME']),
            ('\$HOME', os.environ['HOME']),
            ('\$HOSTNAME', socket.gethostname()),
            ('\$AUTOOAM_VERSION', common.AUTOOAM_VERSION)]
    
    linect = 0
    f1 = open(file1)
    f2 = open(file2)
    for line1 in f1:
        linect += 1
        line2 = f2.readline()
        
        # apply all substitutions on the reference file
        for sub in subs:
            line1 = re.sub(sub[0], sub[1], line1)
            
        # look for the wildcard character and transfer to the target            
        for i in range(0, len(line1)):
            if line1[i] == '*':
                line2 = line2[0:i] + '*' + line2[i+1:]
                
        # look for a terminate character
        for i in range(0, len(line1)):
            if line1[i] == '^':
                line2 = line2[0:i] + '^\n'
        
        if line1 != line2:
            Log.error("Compare of %s vs. %s FAILED" % (file1, file2))
            Log.error("at line %d, *%s* != *%s*" % (linect, line1, line2))
            return False
        
    f1.close()
    f2.close()
    # if passed, delete the target file
    os.remove(file2) 
    return True



