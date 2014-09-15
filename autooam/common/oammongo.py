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
autooam.common.oammongo

Class to manage the connection to the MongoDBinstance used in various aspects of the autooam framework
'''

import emtools.common as common
from pymongo import MongoClient
import bson

class AutoOamMongo(object):
    '''
    This class is a lightweight wrapper to encapsulate connecting to the
    mongodb instance used by autooam.  It uses properties from common.props
    to determine the host, port, and database name to connect to
    '''

    def __init__(self, host='', port=0, db=''):
        '''
        Constructor
        '''
        # get our defaults from the properties that were loaded
        h = common.props['common.oammongo.dbhost']
        p = common.props['common.oammongo.dbport']
        d = common.props['common.oammongo.dbname']
        if host:
            h = host
        if port:
            p = port
        if db:
            d = db
        
        self._connection = MongoClient(h, p)
        self._db = self._connection[d]
        
    def db(self):
        '''Returns a reference to the database.'''
        return self._db

    def getobjectid(self,idnum):
	return bson.objectid.ObjectId(idnum)
