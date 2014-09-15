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
emtools.cluster.emapi

contains:
    class EnterpriseManagerAPI
'''
import urllib2
import json
import time
import emtools.common.logutils as logutils
import emtools.common as common
from datetime import datetime
Log = logutils.getLogger(__name__)

def debug(debuglevel=1):
    handler=urllib2.HTTPHandler(debuglevel=debuglevel)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)

class RequestWithMethod(urllib2.Request):
    def __init__(self, url, method, data=None, headers={}, origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers,origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)
 
class EnterpriseManagerAPI(object):
    '''
    Python wrapper for methods to interact with an Enterprise Manager 
    instance via REST APIs
    '''

    def __init__(self, emhost, emport, cluster_name):
        '''
        Constructor.
        
        @param emhost - hostname (or IP) of the Enterprise Manager (EM) Server
        @param emport - corresponding port of the EM Server
        '''
        self.__emhost = emhost
        self.__emport = emport
        self.__clustername = cluster_name
        self.__id = None
        self.__graphiteurl = None
        if common.props['cluster.emapi.debug']:
            debug()
            self.__debug = True
        else:
            self.__debug = False
        
    def __get_key_data(self, keyfile):
        f = open(keyfile)
        keystr = ''.join(f.readlines())
        return keystr
        
    def __urlopen(self, req, retries=4):
        start = datetime.now()

        attempts = 0
        while attempts < retries:
            try:
                return urllib2.urlopen(req, timeout=common.props['cluster.emapi.timeout'])
            except Exception, exc:
                attempts = attempts + 1
                if attempts == retries:
                    Log.error('Aborting open of %s after %d failed attempts' % (req.get_full_url(), retries))
                    raise exc
                
                # else, sleep the remainder of our timeout
                sleepfor = common.props['cluster.emapi.timeout']-(datetime.now()-start).total_seconds()
                # this is a safeguard just in case the urlopen call takes longer than our timeout
                # value to return
                sleepfor = sleepfor if sleepfor >= 0 else 0
                time.sleep(sleepfor)
                start = datetime.now()
                
    def __get_clusterinfo(self):
        # if we don't know our id yet, we need to look it up in the cluster list
        clusters = self.list_clusters()
        if clusters is None:
            # error already logged above
            return 1
        
        for c in clusters:
            if c['clusterName'] == self.__clustername:
                self.__id = c['clusterId']
                self.__graphiteurl = c['graphiteUrl']
                # success
                return 0

        # failure
        return 1
        
    def get_queries(self, pageindex, pagesize):
        Log.debug('emapi.get_queries(%s,%s)' % (pageindex,pagesize))
        if not self.__id:
            if self.__get_clusterinfo() != 0:
                Log.error('get_queries failed for cluster %s, unable to retrieve clusterId from EM server %s' %\
                          (self.__clustername, self.__emhost))
                return None
        try:
            url = 'http://%s:%s/service/api/v1/clusters/%d/queries?pageIndex=%s&pageSize=%s' %\
                     (self.__emhost, self.__emport, self.__id, pageindex, pagesize)
            f = self.__urlopen(url)
            reply_json = f.read()
            reply = json.loads(reply_json)
            return reply['items']
        except Exception, exc:
            Log.warning('get_queries for cluster %s(id:%d) on EM server %s failed: %s' %\
                        (self.__clustername, self.__id, self.__emhost, exc))
            return None
        
    def get_loads(self, pageindex, pagesize):
        Log.debug('emapi.get_queries(%s,%s)' % (pageindex,pagesize))
        if not self.__id:
            if self.__get_clusterinfo() != 0:
                Log.error('get_loads failed for cluster %s, unable to retrieve clusterId from EM server %s' %\
                          (self.__clustername, self.__emhost))
                return None
        try:
            url = 'http://%s:%s/service/api/v1/clusters/%d/imports?pageIndex=%s&pageSize=%s' %\
                     (self.__emhost, self.__emport, self.__id, pageindex, pagesize)
            f = self.__urlopen(url)
            reply_json = f.read()
            reply = json.loads(reply_json)
            return reply['items']
        except Exception, exc:
            Log.warning('get_loads for cluster %s(id:%d) on EM server %s failed: %s' %\
                        (self.__clustername, self.__id, self.__emhost, exc))
            return None
        
    def graphite_query(self, hostname, metric, start, stop=None):
        Log.debug('emapi.graphite_query(%s,%s,%s,%s)' % (hostname, metric, start, stop))
        if stop == None:
            # stop == None means use current time
            stop = int( time.time() )
            
        if not self.__graphiteurl:
            if self.__get_clusterinfo() != 0:
                Log.error('graphite_query failed for %s.%s, unable to retrieve graphiteUrl from EM server %s' % (hostname, metric, self.__emhost))
                return None
            
        try:
            url = '%s/render?format=raw&target=alias(%s.%s%%2C%%27%%27)&from=%s&until=%s' % (self.__graphiteurl,hostname,metric,start,stop)
            f = self.__urlopen(url)
            reslt = f.read()
            if self.__debug:
                print 'reply:',reslt
            return reslt
        except Exception, exc:
            Log.warning('graphite_query on EM server %s failed: %s' % (self.__emhost, exc))
            return None
        
        
    def list_clusters(self):
        Log.debug('emapi.list_clusters')
        try:
            url = 'http://%s:%s/service/api/v1/clusters' % (self.__emhost, self.__emport)
            f = self.__urlopen(url)
            reply_json = f.read()
            if self.__debug:
                print 'reply:',reply_json
            reply = json.loads(reply_json)
            return reply
        except Exception, exc:
            Log.warning('list_clusters on EM server %s failed: %s' % (self.__emhost, exc))
            return None
        
    def list_modules(self):
        Log.debug('emapi.list_modules')
        if not self.__id:
            if self.__get_clusterinfo() != 0:
                Log.error('list_modules failed for cluster %s, unable to retrieve clusterId from EM server %s' % (self.__clustername, self.__emhost))
                return None
        try:
            url = 'http://%s:%s/service/api/v1/clusters/%d/modules' % (self.__emhost, self.__emport, self.__id)
            f = self.__urlopen(url)
            reply_json = f.read()
            if self.__debug:
                print 'reply:',reply_json
            reply = json.loads(reply_json)
            return reply
        except Exception, exc:
            Log.warning('list_modules for cluster %s(id:%d) on EM server %s failed: %s' % (self.__clustername, self.__id, self.__emhost, exc))
            return None

    def get_cluster_info(self):
        Log.debug('emapi.get_cluster_info')
        if not self.__id:
            if self.__get_clusterinfo() != 0:
                Log.error('get_cluster_info failed for cluster %s, unable to retrieve clusterId from EM server %s' % (self.__clustername, self.__emhost))
                return None
        try:
            url = 'http://%s:%s/service/api/v1/clusters/%d' % (self.__emhost, self.__emport, self.__id)
            f = self.__urlopen(url)
            reply_json = f.read()
            if self.__debug:
                print 'reply:',reply_json
            reply = json.loads(reply_json)
            return reply
        except Exception, exc:
            Log.warning('get_cluster_info for cluster %s(id:%d) on EM server %s failed: %s' % (self.__clustername, self.__id, self.__emhost, exc))
            return None
        
    def delete(self):
        '''Deletes the cluster on the EM server if it exists.'''
        Log.debug('emapi.delete(%s)' % self.__clustername)

        if not self.__id:
            # if we don't know our id yet, we need to look it up in the cluster list
            clusters = self.list_clusters()
            if clusters is None:
                # error already logged above
                Log.error('Unable to delete cluster %s, list_clusters on EM server %s failed' % (self.__clustername, self.__emhost))            
                return 1
            
            found = False
            for c in clusters:
                if c['clusterName'] == self.__clustername:
                    self.__id = c['clusterId']
                    found = True
                    break
            if not found:
                # indicate that the delete failed
                Log.error('Unable to delete cluster %s not found on EM server %s' % (self.__clustername, self.__emhost))
                return 1
            
        try:        
            url = 'http://%s:%s/service/api/v1/clusters/%d' % (self.__emhost, self.__emport, self.__id)
            req = RequestWithMethod(url, 'DELETE')
            req.add_header('Content-Type', 'application/json')
            f = self.__urlopen(req)
            req.get_method = lambda: 'DELETE' # creates the delete method
            reply_json = f.read()
            reply = json.loads(reply_json)
            return 0 if reply['clusterId'] == self.__id else 1
        
        except Exception, exc:
            Log.error('Error deleting cluster %s from EM server %s: %s' % (self.__clustername, self.__emhost, exc))            
            return 1
            
    def attach(self, cluster, probe_host, oam_server, ssh_user, ssh_keyfile, ssh_port=22):
        '''
        Attaches to an existing InfiniDB cluster.  Assumes InfiniDB is 
        installed and running.
        
        @param cluster    - relevant cluster to this operation
        @param probe_host - hostname of a cluster node.  This is the target for getfacts.py
        @param oam_server - hostname of the cluster node that will serve as the oam_server.  
        @param ssh_user   - user used to connect to <probe_host>
        @param ssh_keyfile- ssh key for <ssh_user> or <probe_host>
        @param ssh_port   - ssh port number (OPTIONAL, defaults to 22)
        
        @return int       - 0 on success, 1 on any error
        '''
        Log.debug('emapi.attach(%s)' % self.__clustername)
        
        if common.props['vmi.vagrantvmi.unit-test']:
            return 0
        
        try:
            ssh_key = self.__get_key_data(ssh_keyfile)
            
            data = {
                'host' : probe_host,
                'name' : self.__clustername,
                'sshKey': ssh_key,
                'sshPort': '%d' % ssh_port,
                'sshUser': ssh_user
            }
            
            postdata = json.dumps(data)
            url = 'http://%s:%s/service/api/v1/clusterreport' % (self.__emhost, self.__emport)
            req = urllib2.Request(url, postdata)
            req.add_header('Content-Type', 'application/json')
            Log.info('Executing clusterreport for cluster %s; EM server %s' % (self.__clustername, self.__emhost))
            f = self.__urlopen(req)
        
            reply_json = f.read()
            if self.__debug:
                print '\nreply_json', reply_json
            reply = json.loads(reply_json)
            actionid = reply['id']
            state = reply['state']
        
            url = 'http://%s:%s/service/api/v1/clusterreport/%s' % (self.__emhost, self.__emport, actionid)
            
            while state == 'ongoing':
                time.sleep(5)
                f = self.__urlopen(url)
                reply_json = f.read()
                if self.__debug:
                    print '\nreply_json', reply_json
                reply = json.loads(reply_json)
                state = reply['state']
                
            if state != 'completed':
                Log.error('Error completing clusterreport for cluster %s on EM server %s: %s' % (self.__clustername, self.__emhost, reply['note']))
                return 1
                
            installdata = {
                'roleInfo' : reply['roleInfo'],
                'instanceInfo' : reply['instanceInfo'],
                'clusterInfo' : reply['clusterInfo'],
                'forceInstall' : False,
                'installType' : 'attach'
            }
            installdata['clusterInfo']['oamServer'] = oam_server

            # add um role to each node on "combined" um/pm config
            configspec = cluster.config()   # conf spec used to define db
            if not configspec['rolespec'].has_key('um'):
                for host in installdata['instanceInfo'].keys():
                    role = installdata['instanceInfo'][host]['nodeRoles'][0]
                    if role[0:2] == 'PM' or role[0:2] == 'pm':
                        installdata['instanceInfo'][host]['nodeRoles'].append('UM' + role[2:])
            
            postdata = json.dumps(installdata)
            url = 'http://%s:%s/service/api/v1/clusterinstall' % (self.__emhost, self.__emport)
            req = urllib2.Request(url, postdata)
            req.add_header('Content-Type', 'application/json')
            Log.info('Executing clusterinstall for cluster %s; EM server %s' % (self.__clustername, self.__emhost))
            f = self.__urlopen(req)
        
            reply_json = f.read()
            if self.__debug:
                print '\nreply_json', reply_json
            reply = json.loads(reply_json)
            actionid = reply['id']
            state = reply['state']
        
            url = 'http://%s:%s/service/api/v1/clusterinstall/%s' % (self.__emhost, self.__emport, actionid)
            
            while state == 'ongoing' or state == 'running':
                time.sleep(5)
                f = self.__urlopen(url)
                reply_json = f.read()
                if self.__debug:
                    print '\nreply_json', reply_json
                reply = json.loads(reply_json)
                state = reply['state']

            if state == 'completed' or state == 'complete': #dmc
                Log.info('Successful attach for cluster %s to EM server %s' % (self.__clustername, self.__emhost))
                return 0
            elif state == 'error':
                Log.error('Error attaching cluster %s to EM server %s: %s' % (self.__clustername, self.__emhost, reply['note']))            
                return 1
            else:
                Log.warning('Unrecognized state completing clusterinstall for cluster %s on EM server %s - state is %s' %
                    (self.__clustername, self.__emhost, state))
                return 0
        
        except Exception, exc:
            import traceback
            Log.error('Exception attaching cluster %s to EM server %s: %s' % (self.__clustername, self.__emhost, exc))
            Log.error( traceback.format_exc() )
            return 1
            
    def installdb(self, cluster, ssh_keyfile, ssh_port=22):
        '''
        Use EM to install Infinidb

        @param cluster    - relevant cluster to this operation
        @param ssh_keyfile- ssh key for <ssh_user> or <machines>
        @param ssh_port   - ssh port number (OPTIONAL, defaults to 22)

        @return int       - 0 on success, 1 on any error
        '''
        Log.debug('emapi.installdb(%s)' % self.__clustername)

        if common.props['vmi.vagrantvmi.unit-test']:
            return 0

        configspec = cluster.config()   # conf spec used to define db
        machines   = cluster.machines() # list of db nodes

        try:
            ssh_key = self.__get_key_data(ssh_keyfile)

            hostlist = []
            for m in machines.keys():
                if not m == "em1":
                    hostlist.append( machines[m]['hostname'] )
            data = {
                'hosts'     : hostlist,
                'name'      : self.__clustername,
                'sshKey'    : ssh_key,
                'sshPort'   : '%d' % ssh_port,
                'sshUser'   : configspec['idbuser']
            }

            postdata = json.dumps(data)
            url = 'http://%s:%s/service/api/v1/clusterreport' % (self.__emhost, self.__emport)
            req = urllib2.Request(url, postdata)
            req.add_header('Content-Type', 'application/json')
            Log.info('Executing clusterreport to setup dbinstall; hostlist: %s; cluster %s; EM server %s' %
                (hostlist, self.__clustername, self.__emhost))
            f = self.__urlopen(req)

            reply_json = f.read()
            if self.__debug:
                print '\nreply_json1', reply_json
            reply = json.loads(reply_json)
            actionid = reply['id']
            state = reply['state']

            url = 'http://%s:%s/service/api/v1/clusterreport/%s' % (self.__emhost, self.__emport, actionid)

            Log.info('Wait for clusterreport to setup dbinstall; cluster %s; EM server %s' %
                (self.__clustername, self.__emhost))
            while state == 'ongoing':
                Log.info('Waiting for clusterreport to setup dbinstall; cluster %s; EM server %s' %
                    (self.__clustername, self.__emhost))
                time.sleep(5)
                f = self.__urlopen(url)
                reply_json = f.read()
                if self.__debug:
                    print '\nreply_json2', reply_json
                reply = json.loads(reply_json)
                state = reply['state']

            Log.info('Finished clusterreport to setup dbinstall; cluster %s; EM server %s' %
                (self.__clustername, self.__emhost))
            if state != 'completed':
                Log.error('Error completing clusterreport to setup dbinstall; cluster %s; EM server %s: %s' %
                    (self.__clustername, self.__emhost, reply['note']))
                return 1

            installdata = {
                'roleInfo'     : reply['roleInfo'],
                'instanceInfo' : reply['instanceInfo'],
                'clusterInfo'  : reply['clusterInfo'],
                'forceInstall' : False,
                'installType'  : 'new'
            }

            pmrolespec = configspec['rolespec']['pm']
            installdata['clusterInfo']['dbRootsPerPm']    = pmrolespec['dbroots_per']
            installdata['clusterInfo']['dbrootsPerPm']    = pmrolespec['dbroots_per']

            if not configspec['rolespec'].has_key('um'):
                installdata['clusterInfo']['deploymentType'] = "Combined UM/PM"
            else:
                installdata['clusterInfo']['deploymentType'] = "Separate UM/PM"

            installdata['clusterInfo']['infinidbUser']    = configspec['idbuser']
            idbversion = reply['lookupInfo']['infinidbVersion'][0]
            installdata['clusterInfo']['infinidbVersion'] = idbversion
            if configspec['datdup']:
                installdata['clusterInfo']['storageType'] = "gluster"
            elif configspec['hadoop']:
                installdata['clusterInfo']['storageType'] = "hdfs"
            else:
                installdata['clusterInfo']['storageType'] = "local"
            oamrole = configspec['em']['oamserver_role']
            installdata['clusterInfo']['oamServer']       = cluster.machine(oamrole)['hostname']
            installdata['clusterInfo']['pmQuery']         = configspec['pm_query']
            installdata['clusterInfo']['um_replication']  = False

            for m in machines.keys():
                if not m == "em1":
                    host = machines[m]['hostname']
                    installdata['instanceInfo'][host]['infinidbVersion'] = idbversion
                    installdata['instanceInfo'][host]['nodeRoles']       = [ m ];
                    # add um role to each node on "combined" um/pm config
                    if installdata['clusterInfo']['deploymentType'] == "Combined UM/PM":
                        installdata['instanceInfo'][host]['nodeRoles'].append('UM' + m[2:])

            if self.__debug:
                print '\ninstalldb data clusterInfo: ', installdata['clusterInfo']
                print '\ninstalldb data instanceInfo: ', installdata['instanceInfo']

            postdata = json.dumps(installdata)
            url = 'http://%s:%s/service/api/v1/clusterinstall' % (self.__emhost, self.__emport)
            req = urllib2.Request(url, postdata)
            req.add_header('Content-Type', 'application/json')
            Log.info('Executing clusterinstall to install db; cluster %s; EM server %s' %
                (self.__clustername, self.__emhost))
            f = self.__urlopen(req)

            reply_json = f.read()
            if self.__debug:
                print '\nreply_json3', reply_json
            reply = json.loads(reply_json)
            actionid = reply['id']
            state = reply['state']

            url = 'http://%s:%s/service/api/v1/clusterinstall/%s' % (self.__emhost, self.__emport, actionid)

            while state == 'ongoing' or state == 'running':
                time.sleep(5)
                f = self.__urlopen(url)
                reply_json = f.read()
                if self.__debug:
                    print '\nreply_json4', reply_json
                reply = json.loads(reply_json)
                state = reply['state']

            if state == 'completed' or state == 'complete': #dmc
                Log.info('Successful clusterinstall to install db; cluster %s; EM server %s' %
                    (self.__clustername, self.__emhost))
                return 0
            elif state == 'error':
                Log.error('Error executing clusterinstall to install db; cluster %s; EM server %s: %s' %
                    (self.__clustername, self.__emhost, reply['note']))
                return 1
            else:
                Log.warning('Unrecognized state completing clusterinstall to install db; cluster %s; EM server %s - state is %s' %
                    (self.__clustername, self.__emhost, state))
                return 0
            return 99

        except Exception, exc:
            import traceback
            Log.error('Exception installing InfinidDB through EM; cluster: %s; EM server: %s; %s' %
                (self.__clustername, self.__emhost, exc))
            Log.error( traceback.format_exc() )
            return 1
