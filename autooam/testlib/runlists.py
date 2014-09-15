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
autooam.testlib.runlists

functors for run-list generation.

All config spec functors require exactly 2 arguments:
idbversion - InfiniDB version to use
vmitype    - VMI target

All run-list functors require the InfiniDB version to be passed as a parameter
'''
import sys,inspect
import tests
import configs
import vagboxes
import random
import psutil
import emtools.common as common
from emtools.cluster.configspec import ConfigSpec
from autooam.vmi.versionmgr import VersionManager

def run001(vers, vmitype, num = None, enterprise = True):
    '''Runs basic001 on all configs on all supported boxtypes.'''
    runlist = []
    if vmitype == 'vagrant':
        for b in vagboxes.list_all():
            for c in configs.list_all():            
                cfg = configs.call_by_name(c[0], vers, b)
                cfg['enterprise'] = enterprise
                runlist.append( (cfg, 'vagrant', tests.basic001() ) )        

    return _random_subset(runlist,num)

def run002(vers, vmitype, num = None, enterprise = True):
    '''Runs basic002 on all configs on all supported boxtypes.'''
    runlist = []
    if vmitype == 'vagrant':
        for b in vagboxes.list_all():
            for c in configs.list_all():
                cfg = configs.call_by_name(c[0], vers, b)
                cfg['enterprise'] = enterprise
                runlist.append( (cfg, 'vagrant', tests.basic002() ) )

    return _random_subset(runlist,num)
    
def run001_nonroot(vers, vmitype, num = None, enterprise = True):
    '''Runs basic001 on all configs with a non-root calpont user on all supported boxtypes.'''
    runlist = []
    if vmitype == 'vagrant':
        for b in vagboxes.list_all():
            for c in configs.list_all():            
                cfg = configs.call_by_name(c[0], vers, b)
                cfg['idbuser'] = 'calpont'
                cfg['enterprise'] = enterprise
                runlist.append( (cfg, 'vagrant', tests.basic001() ) )        

    return _random_subset(runlist,num)

def run_random_basic002(vers, vmitype, num = None, enterprise = True):
    '''Runs basic002 on a randomly generated config. 
       Note that the enterprise parameter is intentionally ignored.'''
    
    cfgs = [
             ( 'multi_2umpm_combo', 0.5 ),
             ( 'multi_1um_2pm', 0.5 ),
             ]
    if ConfigSpec._version_greaterthan(vers,'3.5.3'):
        cfgs.append( ('singlenode', 0.5) )
    
    idbusers = [
                ( 'root', 0.6 ),
                ( 'calpont', 0.4 )
               ]
    datdups   = [
             ( True, 0.2 ),
             ( False, 0.8 )
             ]
    binaries  = [
             ( True, 0.2 ),
             ( False, 0.8 )
             ]
    storages = [ 
             ('internal', 0.5 ),
             ('external', 0.5 )
             ]
    enterprises  = [
             ( True, 0.5 ),
             ( False, 0.5 )
             ]
    pmquerys  = [
             ( True, 0.5 ),
             ( False, 0.5 )
             ]
    emroles = [
             ( 'um1', 0.7),
             ( 'em1', 0.2),
             ( 'pm1', 0.1)
             ]
    
    runlist = []
    if num <= 0:
        # for this runlist we always want to generate at least one
        num = 1
    for i in range (0, num):    
        boxtype = _choose_rand_boxtype()
        cfgname = _choose_weighted(cfgs)
        cfg = configs.call_by_name(cfgname, vers, boxtype)
        idbuser = _choose_weighted(idbusers)
        cfg['idbuser'] = idbuser
        enterprise = _choose_weighted(enterprises)
        cfg['enterprise'] = enterprise

        # technically we supported datdup since 3.5.1 but are rereleasing with a different 
        # strategy for installation/integration in 4.0
        if ConfigSpec._version_greaterthan(vers,'4.0.0-0') and \
            vagboxes.datdup_support(boxtype) and \
            cfg['rolespec']['pm']['count'] > 1 and \
            enterprise == True:
            datdup = _choose_weighted(datdups)
        else:
            datdup = False
        # TODO: due to various InfiniDB bugs, datdup (i.e. glusterfs) support is
        # currently broken so hardcoding this to false.
        #cfg['datdup'] = datdup
        cfg['datdup'] = False
        
        # EM related checks
        if common.props['cluster.cluster.eminvm'] and not vagboxes.em_support(boxtype):
            # this can happen in the emboxonly flag is not set and a "legacy" box gets chosen.
            # in that case we just reset the 'em' field to None to bypass any EM in this test
            cfg['em'] = None
        elif common.props['cluster.cluster.eminvm']:
            # randomly vary which node the EM is assugned to
            cfg['em']['role'] = _choose_weighted(emroles)
        
        if idbuser == 'root':
            cfg['binary'] = _choose_weighted(binaries)
        if ConfigSpec._version_greaterthan(vers,'4.5.0-0'):
            cfg['pm_query'] = _choose_weighted(pmquerys)

        # for unknown reasons there is an issue with the external storage
        # configuration on the smaller of the 3 initial autooam machines
        # (srvautooam, srvoam1, srvoam2).  For now, we will avoid running
        # external storage on srvautooam by checking system memory.  NOTE:
        # the amount of memory may or may not have anything at all to do
        # with the manifestation of the issue
    
        # datdup only works with internal storage, so don't attempt an override here
        if not datdup and psutil.virtual_memory().total >= 16825044992L:
            cfg['storage'] = _choose_weighted(storages)
            
        runlist.append( (cfg, 'vagrant', tests.basic002() ) )
    return runlist

def run_chef_smoketest(vers, vmitype, num = None, enterprise = True):
    '''Run all the major config variations on varied platforms.'''
    
    # this is a standard root package install
    cfg = configs.multi_2umpm_combo(vers)
    cfg['boxtype'] = 'cal-debian6'
    cfg['upgrade'] = 'Latest'
    cfg['enterprise'] = enterprise
    runlist = [ (cfg, 'vagrant', tests.upgrade001()) ]
    
    # now a root user binary install
    cfg = configs.multi_2umpm_combo(vers)
    cfg['binary'] = True
    cfg['boxtype'] = 'cal-lucid64'
    cfg['upgrade'] = 'Latest'
    cfg['enterprise'] = enterprise
    cfg['em'] = None # guarantee no EM since this is a "legacy" boxtype
    runlist.append( (cfg, 'vagrant', tests.upgrade001()) )
    
    # now non-root user
    cfg = configs.multi_1um_2pm(vers)
    cfg['idbuser'] = 'calpont'
    cfg['boxtype'] = 'cal-precise64'
    cfg['upgrade'] = 'Latest'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.upgrade001()) )

    # now root user datdup
    cfg = configs.multi_1um_2pm(vers)
    cfg['datdup'] = True
    cfg['boxtype'] = 'cal-centos6'
    cfg['upgrade'] = 'Latest'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.upgrade001()) )

    # now non-root user datdup
    cfg = configs.multi_2umpm_combo(vers)
    cfg['idbuser'] = 'calpont'
    cfg['datdup'] = True
    cfg['boxtype'] = 'cal-centos6'
    cfg['upgrade'] = 'Latest'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.upgrade001()) )

    # now single node root
    cfg = configs.singlenode(vers)
    cfg['boxtype'] = 'cal-centos6'
    cfg['upgrade'] = 'Latest'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.upgrade001()) )

    # now single node non-root
    cfg = configs.singlenode(vers)
    cfg['idbuser'] = 'calpont'
    cfg['boxtype'] = 'cal-precise64'
    cfg['upgrade'] = 'Latest'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.upgrade001()) )

    return runlist

def run_boxtest(vers, vmitype, num = None, enterprise = True):
    '''Run all boxes variations with single node configs and minimal other variation.'''
    runlist = []
    
    # centos6
    cfg = configs.singlenode(vers)
    cfg['boxtype'] = 'cal-centos6'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.basic002()) )

    # debian6
    cfg = configs.singlenode(vers)
    cfg['idbuser'] = 'calpont'
    cfg['boxtype'] = 'cal-debian6'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.basic002()) )

    # debian7
    cfg = configs.singlenode(vers)
    cfg['binary'] = True
    cfg['boxtype'] = 'cal-debian7'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.basic002()) )

    # precise64
    cfg = configs.singlenode(vers)
    cfg['boxtype'] = 'cal-precise64'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.basic002()) )

    # trusty64
    cfg = configs.singlenode(vers)
    cfg['idbuser'] = 'calpont'
    cfg['boxtype'] = 'cal-trusty64'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.basic002()) )

    return runlist

def run_module_failover(vers, vmitype, num = None, enterprise = True):
    '''Runs moduleFailover on all configs on all supported boxtypes.'''
    runlist = []
  
    # root user
    cfg = configs.multi_1um_2pm(vers)
    cfg['boxtype'] = 'cal-precise64'
    cfg['storage'] = 'external'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.moduleFailover()) )

    cfg = configs.multi_2umpm_combo(vers)
    cfg['boxtype'] = 'cal-centos6'
    cfg['storage'] = 'external'
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.moduleFailover()) )

    cfg = configs.multi_1um_2pm(vers)
    cfg['boxtype'] = 'cal-debian6'
    cfg['storage'] = 'external'
    cfg['binary'] = True
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.moduleFailover()) )

    cfg = configs.multi_1um_2pm(vers)
    cfg['boxtype'] = 'cal-centos6'
    cfg['datdup'] = True
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.moduleFailover()) )

    cfg = configs.multi_1um_2pm(vers)
    cfg['boxtype'] = 'cal-centos6'
    cfg['datdup'] = True
    cfg['binary'] = True
    cfg['enterprise'] = enterprise
    runlist.append( (cfg, 'vagrant', tests.moduleFailover()) )

    # non-root user
    cfg = configs.multi_2umpm_combo(vers)
    cfg['idbuser'] = 'calpont'
    cfg['boxtype'] = 'cal-centos58'
    cfg['storage'] = 'external'
    cfg['enterprise'] = enterprise
    cfg['em'] = None # guarantee no EM since this is a "legacy" boxtype
    runlist.append( (cfg, 'vagrant', tests.moduleFailover()) )

    cfg = configs.multi_1um_2pm(vers)
    cfg['idbuser'] = 'calpont'
    cfg['boxtype'] = 'cal-lucid64'
    cfg['storage'] = 'external'
    cfg['enterprise'] = enterprise
    cfg['em'] = None # guarantee no EM since this is a "legacy" boxtype
    runlist.append( (cfg, 'vagrant', tests.moduleFailover()) )

    return runlist

def run_nightly_regression(vers, vmitype, num = None, enterprise = True):
    '''Runs Nightly Regression Test'''

    runlist1 = run_random_basic002(vers=vers, vmitype=vmitype, num=num, enterprise=enterprise)

    runlist2 = run_module_failover(vers=vers, vmitype=vmitype, enterprise=enterprise)

    runlist3 = run_upgrade_suite(vers=vers, vmitype=vmitype, enterprise=enterprise)

    return runlist1+runlist2+runlist3

def run_nightly_regression_3x(vers, vmitype, num = None, enterprise = True):
    '''Runs Nightly Regression Test'''

    runlist1 = run_random_basic002(vers=vers, vmitype=vmitype, num=num, enterprise=enterprise)

    runlist2 = run_upgrade_suite(vers=vers, vmitype=vmitype, enterprise=enterprise)

    return runlist1+runlist2



def run_upgrade_suite(vers, vmitype, num = None, enterprise = True):
    '''Runs standard set up upgrade tests for version under test.'''
    if common.props['cluster.cluster.use_em_for_dbinstall']:
        raise Exception('run_upgrade_suite does not support cluster.cluster.use_em_for_dbinstall!')
    
    runlist = []
    
    vmgr = VersionManager()
    
    baselist = common.props['testlib.runlists.upgradefrom']
    streams = baselist.split(',')
    for s in streams:
        # if the stream is the same as the version under test
        # then we need to grab the last release on this stream
        minusone = False if not vers.find(s) == 0 else True
        basever = s
        try:
            basever = vmgr.latest_release_vers(s, minusone)
        except:
            # if we get here, we assume that s is a specific version 
            # that the user wants to upgrade from
            pass
        
        if basever and ConfigSpec._version_greaterthan(vers,basever):
            if ConfigSpec._version_greaterthan(basever, '3.5.1-6' ) or \
                ConfigSpec._version_greaterthan('3.0.0-0', basever ):
                # anything between 3.0 and 3.5.1-5 does not support single server 
                # installs because of the postconfigure race issue.
                
                cfg = configs.singlenode(basever)
                cfg['boxtype'] = 'cal-centos58'
                cfg['binary'] = True
                cfg['upgrade'] = vers
                cfg['enterprise'] = enterprise
                cfg['em'] = None # guarantee no EM since this is a "legacy" boxtype
                runlist.append( (cfg, 'vagrant', tests.upgrade001()) )
    
                cfg = configs.singlenode(basever)
                cfg['boxtype'] = 'cal-debian6'
                cfg['upgrade'] = vers
                cfg['enterprise'] = enterprise
                if not ConfigSpec._version_greaterthan(basever, '4.5.1-3' ):
                    # will not repeat this comment each time, but we can use the EM
                    # here as long as it is in attach mode and we are on a supported
                    # version
                    cfg['em'] = None
                runlist.append( (cfg, 'vagrant', tests.upgrade001()) )
    
                cfg = configs.singlenode(basever)
                cfg['boxtype'] = 'cal-centos6'
                cfg['upgrade'] = vers
                cfg['enterprise'] = enterprise
                if not ConfigSpec._version_greaterthan(basever, '4.5.1-3' ):
                    cfg['em'] = None
                runlist.append( (cfg, 'vagrant', tests.upgrade001()) )
    
                cfg = configs.singlenode(basever)
                cfg['boxtype'] = 'cal-precise64'
                cfg['upgrade'] = vers
                cfg['enterprise'] = enterprise
                if not ConfigSpec._version_greaterthan(basever, '4.5.1-3' ):
                    cfg['em'] = None
                runlist.append( (cfg, 'vagrant', tests.upgrade001()) )

                if ConfigSpec._version_greaterthan(basever, '3.5.1-5' ):
                    # binary install supported after 3.5.1-5
                    cfg = configs.singlenode(basever)
                    cfg['boxtype'] = 'cal-centos6'
                    cfg['idbuser'] = 'calpont'
                    cfg['upgrade'] = vers
                    cfg['enterprise'] = enterprise
                    if not ConfigSpec._version_greaterthan(basever, '4.5.1-3' ):
                        cfg['em'] = None
                    runlist.append( (cfg, 'vagrant', tests.upgrade001()) )
                    
        
            if not s == '2.2':
                # not going to support multi-node upgrades from 2.2 because if 
                # differences in the Calpont.xml.  Could support, but would need
                # to switch to using a postconfigure.in on the upgrade run of
                # postconfigure
                cfg = configs.multi_1um_2pm(basever)
                cfg['boxtype'] = 'cal-centos6'
                cfg['binary'] = True
                cfg['upgrade'] = vers
                cfg['enterprise'] = enterprise
                if not ConfigSpec._version_greaterthan(basever, '4.5.1-3' ):
                    cfg['em'] = None
                runlist.append( (cfg, 'vagrant', tests.upgrade001()) )
    
                cfg = configs.multi_2umpm_combo(basever)
                cfg['boxtype'] = 'cal-centos6'
                cfg['upgrade'] = vers
                cfg['enterprise'] = enterprise
                if not ConfigSpec._version_greaterthan(basever, '4.5.1-3' ):
                    cfg['em'] = None
                runlist.append( (cfg, 'vagrant', tests.upgrade001()) )
    
                cfg = configs.multi_1um_2pm(basever)
                cfg['boxtype'] = 'cal-debian6'
                cfg['upgrade'] = vers
                cfg['enterprise'] = enterprise
                if not ConfigSpec._version_greaterthan(basever, '4.5.1-3' ):
                    cfg['em'] = None
                runlist.append( (cfg, 'vagrant', tests.upgrade001()) )

                if ConfigSpec._version_greaterthan(basever, '3.5.1-5' ):
                    cfg = configs.multi_2umpm_combo(basever)
                    cfg['boxtype'] = 'cal-precise64'
                    cfg['idbuser'] = 'calpont'
                    cfg['upgrade'] = vers
                    cfg['enterprise'] = enterprise
                    if not ConfigSpec._version_greaterthan(basever, '4.5.1-3' ):
                        cfg['em'] = None
                    runlist.append( (cfg, 'vagrant', tests.upgrade001()) )

    return runlist

def _base_hadoop_1um_2pm_config( vers, boxtype, enterprise ):
    cfg = configs.multi_1um_2pm(vers)
    cfg['name'] = '1um_2pm_hadoop'
    cfg['boxtype'] = boxtype
    cfg['hadoop'] = {
        "instance-templates" : "1 hadoop-namenode+hadoop-jobtracker,2 hadoop-datanode+hadoop-tasktracker",
        "templates-namenode" : "um1",
        "templates-datanode" : "pm1+pm2"
        }
    cfg['enterprise'] = enterprise
    cfg['rolespec']['pm']['memory'] = 8192
    cfg['rolespec']['um']['memory'] = 8192
    return cfg 
    
def run_hadoop_basic(vers, vmitype, num = None, enterprise = True):
    '''Run basic002 on the supported Hadoop configurations.'''
    
    # standard root package installs
    cfg = _base_hadoop_1um_2pm_config( vers, 'cal-centos6', enterprise ) 
    runlist = [ (cfg, 'vagrant', tests.basic002()) ]
    runlist.append( (cfg, 'vagrant', tests.moduleFailover(testpm1_fail = False)) )

    cfg = _base_hadoop_1um_2pm_config( vers, 'cal-precise64', enterprise ) 
    runlist.append( (cfg, 'vagrant', tests.basic002()) )
    runlist.append( (cfg, 'vagrant', tests.moduleFailover(testpm1_fail = False)) )

    # standard root binary installs
    cfg = _base_hadoop_1um_2pm_config( vers, 'cal-centos6', enterprise ) 
    cfg['binary'] = True
    runlist.append( (cfg, 'vagrant', tests.basic002()) )
    runlist.append( (cfg, 'vagrant', tests.moduleFailover(testpm1_fail = False)) )

    cfg = _base_hadoop_1um_2pm_config( vers, 'cal-precise64', enterprise ) 
    cfg['binary'] = True
    runlist.append( (cfg, 'vagrant', tests.basic002()) )
    runlist.append( (cfg, 'vagrant', tests.moduleFailover(testpm1_fail = False)) )
    
    return runlist

def run_nightly_with_hadoop(vers, vmitype, num = None, enterprise = True):
    '''Runs Nightly Regression Test'''

    runlist1 = run_random_basic002(vers=vers, vmitype=vmitype, num=num, enterprise=enterprise)

    runlist2 = run_hadoop_basic(vers=vers, vmitype=vmitype, enterprise=enterprise)

    return runlist1+runlist2

def list_all():
    register = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj) and name != 'list_all' and name != 'call_by_name' and name[0] != '_':
            register.append((obj.func_name,obj.__doc__, obj))
    return register

def call_by_name(name, idbversion, vmitype, num=0, enterprise=True):
    thismodule = sys.modules[__name__]
    fn = getattr(thismodule,name)
    return fn(idbversion, vmitype, num=num, enterprise=enterprise)

def _random_subset(runlist, numrand):
    if numrand >= len(runlist) or numrand == 0:
        return runlist
    
    sublist = []
    indices = []
    while len(sublist) < numrand:
        try_ = random.randint(0, len(runlist)-1)
        try:
            indices.index(try_)
        except:
            # this is good, it means we don't have it
            indices.append(try_)
            sublist.append(runlist[try_])
    return sublist
    
def _choose_rand_boxtype():
    if common.props['testlib.runlists.embox_only']:
        boxes = [
                 ( 'cal-centos6', 0.4 ),
                 ( 'cal-precise64', 0.15 ),
                 ( 'cal-trusty64', 0.15 ),
                 ( 'cal-debian6', 0.15 ),
                 ( 'cal-debian7', 0.15 )
                ]
    else:
        boxes = [
                 ( 'cal-centos58', 0.05 ),
                 ( 'cal-lucid64', 0.05 ),
                 ( 'cal-centos6', 0.35 ),
                 ( 'cal-precise64', 0.15 ),
                 ( 'cal-trusty64', 0.1 ),
                 ( 'cal-debian6', 0.15 ),
                 ( 'cal-debian7', 0.15 )
                ]
    
    return _choose_weighted(boxes)

def _choose_weighted(weightlist):
    total = 0.0
    
    # compute the total weights in case not 1.0
    for w in weightlist:
        total += w[1]
        
    # scale our random number by the factor        
    sample = random.random() * total;

    weightsofar = 0.0    
    for w in weightlist:
        weightsofar += w[1]
        if sample <= weightsofar:
            return w[0]
    
