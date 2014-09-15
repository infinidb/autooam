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
autooam.cluster.rundb

A class that interacts with a MongoDB instance to track running clusters
'''

from cluster import Cluster
from autooam.vmi.vmi import VMI
from autooam.common.oammongo import AutoOamMongo
import json
from emtools.cluster.configspec import ConfigSpec
import emtools.common.logutils as logutils
Log = logutils.getLogger(__name__)

class ClusterMgr(object):
    '''
    The ClusterMgr provides an interface to create and remove clusters
    as well as list active clusters.  Internally it uses a MongoDB
    instance for persistence
        
    __init__      - constructor that connects to the database
    list_clusters - list all clusters
    alloc_new     - allocate a new cluster instance using a ConfigSpec
    remove        - removes a cluster
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._dbcon = AutoOamMongo()
        self._db = self._dbcon.db().clusters
                 
    def list_clusters(self):
        '''Returns the list of clusters as (name, id) tuples.'''
        ret = []
        for c in self._db.find(): 
	    name='ERROR -no name'
	    try:
        	name=c['name'] 
	    except:
 		pass
            ret.append( (str(name), str(c['_id'])) )
        return ret
    
    def alloc_new(self,name, configspec, vmitype, chefmode=True):
        '''Allocates a new cluster.
        
        @param name - name for the cluster (ideally unique)
        @param configspec - a ConfigSpec instance
        @param vmitype - string specifying vmi type (supported: 'vagrant')
        '''
        cid = self._db.insert({})        
        try:
            configspec.validate()
            cluster = Cluster( name, configspec, cid, chefmode=chefmode )
            VMI.Create(vmitype, cluster)
            self._db.update( 
                            { '_id' : cluster.id() }, 
                            { u'name' : name,
                              u'config' : configspec.jsonmap, 
                              u'vmi' : cluster.get_vmi().jsonmap(), 
                              u'machines' : cluster.machines()} )
        except Exception as exc:
            import traceback
            Log.error('Cluster creation failed: %s' % exc)
            Log.error( traceback.format_exc() )
            self._db.remove( { '_id' : cid } )
            raise Exception('Failed to create cluster: %s' % name)
        
        return cluster
    
    def attach(self,name):
        '''Attempts to attach to an existing cluster.
        
        @param name - cluster name to attach to
                          
        raises eusterception of number found is not found
        '''
        try:
            cursor = self._db.find({'name' : name})
            defn = cursor[0]
            cluster = Cluster(defn['name'], ConfigSpec(json.dumps(defn['config'])), defn['_id'],machines=defn['machines'], attach=True)
            VMI.Attach(cluster, defn['vmi'])
            return cluster
        except Exception as err:
            raise Exception("Error attaching to cluster %s: %s!" % (name,err))
    
    def destroy(self,cluster):
        '''Destroys the cluster and removes from the database.  DESTRUCTIVE operation.'''
        crit = { '_id' : cluster.id() }
        clusterdefn = self._db.find_one( crit )
        if not clusterdefn:
            Log.error("Cluster id %s not in database!" % cluster.id())
        else:
            try:
                cluster.destroy()
                self._db.remove( crit )
                return True
            except Exception as err:
                Log.error("Unable to destroy cluster: %s" % err)

        return False

    def destroy_by_id(self,idnum):
        '''Destroys the cluster and removes from the database.  DESTRUCTIVE operation.'''
	crit = { '_id' : self._dbcon.getobjectid( idnum ) }
        clusterdefn = self._db.find_one( crit )
        if not clusterdefn:
            Log.error("id %s not in database!" % idnum)
        else:
            try:
                self._db.remove( crit )
                return True
            except Exceptionoammongo.py  as err:
                Log.error("Unable to destroy cluster by id: %s" % err)

        return False

