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
Created on Dec 18, 2012

@author: rtw
'''
import unittest
from emtools.cluster.configspec import ConfigSpec
import testutils
import test_common
import emtools.common as common
from autooam.cluster.clustermgr import ClusterMgr
from autooam.common.oammongo import AutoOamMongo
import os,sys

class ClusterMgrTest(unittest.TestCase):


    def setUp(self):
        # clean out the test db
        dbcon = AutoOamMongo()
        dbcon.db().clusters.remove()
        dbcon.db().allocs.remove()

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-5", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 1
                },
                "um" : {
                    "count" : 1,
                    "memory" : 2048
                }
              }
            }
            """
        self._defcfg = ConfigSpec(s)

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-5", 
            "boxtype" : "cal-precise64",
            "idbuser" : "calpont",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 1
                },
                "um" : {
                    "count" : 1,
                    "memory" : 2048
                }
              }
            }
            """
        self._nonrootcfg = ConfigSpec(s)

        # cluster used to test external dbroots
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-5", 
            "boxtype"    : "cal-centos6",
            "storage"    : "external",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1
                }
              }
            }
            """
        self._extcfg = ConfigSpec(s)

        # cluster used to test pm_query
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "4.5.0-1", 
            "boxtype"    : "cal-precise64",
            "binary"     : true,
            "pm_query"   : true,
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1
                }
              }
            }
            """
        self._pmquerycfg = ConfigSpec(s)

    def tearDown(self):
        pass

    
    def testSubnetAlloc(self):        
        #print '++++++++++ DEBUG: starting testSubnetAlloc'
        mgr = ClusterMgr()
        c1 = mgr.alloc_new('testsub1',self._defcfg,'vagrant')
        c2 = mgr.alloc_new('testsub2',self._defcfg,'vagrant')
        
        self.assertEqual( c1.get_vmi()._subnet, '192.168.1' )
        self.assertEqual( c2.get_vmi()._subnet, '192.168.2' )
        
        mgr.destroy(c1)
        mgr.destroy(c2)

    def testClusterFiles(self):        
        #print '++++++++++ DEBUG: Starting testClusterFiles'
        mgr = ClusterMgr()
        
        c = mgr.alloc_new('test1',self._defcfg,'vagrant')
        ref_file = '%s/test1-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))
        ref_file = '%s/test1-postconfigure.in' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._pfile))
        
        self.assertEqual( mgr.list_clusters()[0][0], 'test1' )
        
        c.destroy_files_only()

    def testAttach(self):        
        #print '++++++++++ DEBUG: starting testAttach'
        mgr = ClusterMgr()
        
        c = mgr.alloc_new('testAttach',self._defcfg,'vagrant')
        c1 = mgr.attach( 'testAttach' )
        self.assertEquals( c1.id() , c.id() )

        with self.assertRaisesRegexp(Exception,"Error attaching to cluster.*"):        
            c2 = mgr.attach( 'no-cluster' )
                
        mgr.destroy(c)
        # no need to destroy c1 as it will not have been created

    def testDupName(self):        
        #print '++++++++++ DEBUG: starting testDupName'
        mgr = ClusterMgr()
        
        c1 = mgr.alloc_new('testdup',self._defcfg,'vagrant')
        c2 = mgr.alloc_new('testdup',self._defcfg,'vagrant')
                
        mgr.destroy(c1)
        mgr.destroy(c2)

    def testComboConfigMachineAccess(self):        
        #print '++++++++++ DEBUG: starting testComboConfigMachineAccess'
        mgr = ClusterMgr()
        
        s = """{
            "name" : "combo-cluster",
            "idbversion" : "3.5.1-5", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                }
              }
            }
            """
        cfg = ConfigSpec(s)        
        c = mgr.alloc_new('combo',cfg,'vagrant')
        
        # this should get aliased to pm1
        c.machine('um1')
        # this still doesn't exist even after the alias
        with self.assertRaisesRegexp(ValueError,"Machine name.*not in.*"):                
            c.machine('um3') 
                
        mgr.destroy(c)
        
    def testAllocFailure(self):        
        #print '++++++++++ DEBUG: starting testAllocFailure'
        mgr = ClusterMgr()
        
        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-5", 
            "rolespec" : {
                "pm" : {
                    "count" : 1,
                    "dbroots_per" : 1
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        with self.assertRaisesRegexp(Exception,"Failed to create cluster"):        
            c1 = mgr.alloc_new('testdup',cfg,'vagrant')
                
    def testClusterFilesNonRoot(self):        
        #print '++++++++++ DEBUG: starting testClusterFilesNonRoot'
        mgr = ClusterMgr()
        
        c = mgr.alloc_new('test1',self._nonrootcfg,'vagrant')
        ref_file = '%s/testnonroot-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))
        ref_file = '%s/testnonroot-postconfigure.in' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._pfile))
        
        self.assertEqual( mgr.list_clusters()[0][0], 'test1' )
        
        c.destroy_files_only()

    def testValidateFailure(self):        
        #print '++++++++++ DEBUG: starting testValidateFailure'
        mgr = ClusterMgr()
        
        # this should fail because datdup not supported in 3.5.0-3
        s = """{
            "name" : "combo-cluster",
            "idbversion" : "3.5.0-3", 
            "boxtype" : "cal-centos6",
            "datdup" : true,
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        with self.assertRaisesRegexp(Exception,"Failed to create cluster"):        
            c1 = mgr.alloc_new('testdup',cfg,'vagrant')

        # test invalid combination; external storage with datdup
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "4.0.0-0",
            "boxtype"    : "cal-centos6",
            "storage"    : "external",
            "datdup"     : true,
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count"  : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        with self.assertRaisesRegexp(Exception,"Failed to create cluster"):
            c1 = mgr.alloc_new('testdupExternal',cfg,'vagrant')

    def testClusterFilesExt(self):
        '''Test cluster with external dbroots'''
        #print '++++++++++ DEBUG: starting testClusterFilesExt'
        mgr = ClusterMgr()

        c = mgr.alloc_new('testext',self._extcfg,'vagrant')
        ref_file = '%s/testext-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))
        ref_file = '%s/testext-postconfigure.in' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._pfile))

        self.assertEqual( mgr.list_clusters()[0][0], 'testext' )

        c.destroy_files_only()

    def testClusterFiles22(self):
        '''Test cluster with version 2.2'''
        #print '++++++++++ DEBUG: starting testClusterFiles22'
        mgr = ClusterMgr()

        s = """{
            "name" : "a-cluster",
            "idbversion" : "2.2.11-1", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                }
              }
            }
            """
        cfg = ConfigSpec(s)

        c = mgr.alloc_new('test22',cfg,'vagrant')
        ref_file = '%s/test22-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))
        ref_file = '%s/test22-postconfigure.in' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._pfile))

        self.assertEqual( mgr.list_clusters()[0][0], 'test22' )

        c.destroy_files_only()

    def testClusterFilesUpgrade(self):
        '''Test cluster with upgrade version specified'''
        #print '++++++++++ DEBUG: starting testClusterFilesUpgrade'
        mgr = ClusterMgr()

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-5", 
            "boxtype" : "cal-precise64",
            "upgrade" : "Latest",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 1
                },
                "um" : {
                    "count" : 1,
                    "memory" : 2048
                }
              }
            }
            """
        cfg = ConfigSpec(s)

        c = mgr.alloc_new('testupg',cfg,'vagrant')
        ref_file = '%s/testupg-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))
        ref_file = '%s/testupg-postconfigure.in' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._pfile))

        self.assertEqual( mgr.list_clusters()[0][0], 'testupg' )

        c.destroy_files_only()

    def testDatdup(self):
        '''Test cluster with datdup specified'''
        #print '++++++++++ DEBUG: starting testDatdup'
        mgr = ClusterMgr()

        s = """{
            "name" : "a-cluster",
            "idbversion" : "4.0.0-0", 
            "boxtype" : "cal-precise64",
            "datdup" : true,
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 1
                },
                "um" : {
                    "count" : 1,
                    "memory" : 2048
                }
              }
            }
            """
        cfg = ConfigSpec(s)

        c = mgr.alloc_new('testdatdup',cfg,'vagrant')
        self.assertEqual( mgr.list_clusters()[0][0], 'testdatdup' )

        mgr.destroy(c)

    def testClusterFilesHadoop(self):
        '''Test cluster with hadoop specified'''
        #print '++++++++++ DEBUG: starting testClusterFilesHadoop'
        mgr = ClusterMgr()

        s = """{
            "name" : "a-cluster",
            "idbversion" : "Latest", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "memory" : 1024,
                    "dbroots_per" : 1
                },
                "um" : {
                    "count" : 1,
                    "memory" : 2048
                }
              },
           "hadoop" : {
            "instance-templates" : "1 hadoop-namenode+hadoop-jobtracker,2 hadoop-datanode+hadoop-tasktracker"
              }              
            }
            """
        cfg = ConfigSpec(s)

        c = mgr.alloc_new('testhadoop',cfg,'vagrant')
        ref_file = '%s/testhadoop-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))
        ref_file = '%s/testhadoop-postconfigure.in' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._pfile))

        self.assertEqual( mgr.list_clusters()[0][0], 'testhadoop' )

        c.destroy_files_only()

    def testClusterFilesHadoopValidation(self):
        '''Test cluster with hadoop validation error'''
        #print '++++++++++ DEBUG: starting testClusterFilesHadoopValidation'
        mgr = ClusterMgr()

        # test without mandatory config specified
        s = """{
            "name" : "a-cluster",
            "idbversion" : "Latest",
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "memory" : 1024,
                    "dbroots_per" : 1
                },
                "um" : {
                    "count" : 1,
                    "memory" : 2048
                }
              },
           "hadoop" : {
              "version" : "1.2.1"
              }
            }
            """
        cfg = ConfigSpec(s)

        with self.assertRaisesRegexp(Exception,"Failed to create cluster: testhadoop.*"):
            c = mgr.alloc_new('testhadoop',cfg,'vagrant')

    def testClusterFilesStandard(self):
        '''Test cluster with non-enterprise version specified'''
        #print '++++++++++ DEBUG: starting testClusterFilesStandard'
        mgr = ClusterMgr()

        s = """{
            "name" : "a-cluster",
            "idbversion" : "4.0.0-1", 
            "boxtype" : "cal-precise64",
            "enterprise" : false,
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "memory" : 1024,
                    "dbroots_per" : 1
                },
                "um" : {
                    "count" : 1,
                    "memory" : 2048
                }
              }
            }
            """
        cfg = ConfigSpec(s)

        c = mgr.alloc_new('teststd',cfg,'vagrant')
        ref_file = '%s/teststd-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))

        self.assertEqual( mgr.list_clusters()[0][0], 'teststd' )

        c.destroy_files_only()

    def testPmQuery(self):
        '''Test cluster with PMQuery'''
        #print '++++++++++ DEBUG: starting testPMQuery'
        mgr = ClusterMgr()

        c = mgr.alloc_new('testpmquery', self._pmquerycfg,'vagrant')
        ref_file = '%s/testpmquery-postconfigure.in' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._pfile))

        c.destroy_files_only()

    def testClusterFilesEM(self):
        '''Test cluster with EM present'''
        #print '++++++++++ DEBUG: starting testClusterFilesStandard'
        mgr = ClusterMgr()

        s = """{
            "name" : "em-cluster",
            "idbversion" : "4.5.0-1", 
            "binary" : true,
            "boxtype" : "cal-centos6",
            "em" : { "present" : true },
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "memory" : 1024,
                    "dbroots_per" : 1
                }
              }
            }
            """
        cfg = ConfigSpec(s)

        c = mgr.alloc_new('testem1',cfg,'vagrant')
        ref_file = '%s/testem1-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))

        self.assertEqual( mgr.list_clusters()[0][0], 'testem1' )

        c.destroy_files_only()

    def testClusterFilesEMinVM(self):
        '''Test cluster with EM present'''
        #print '++++++++++ DEBUG: starting testClusterFilesEMinVM'
        mgr = ClusterMgr()

        s = """{
            "name" : "em-cluster",
            "idbversion" : "4.5.0-1", 
            "binary" : true,
            "boxtype" : "cal-precise64",
            "em" : { "present" : true, "invm" : true, "role" : "em1" },
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "memory" : 1024,
                    "dbroots_per" : 1
                }
              }
            }
            """
        cfg = ConfigSpec(s)

        c = mgr.alloc_new('testeminvm',cfg,'vagrant')
        ref_file = '%s/testeminvm-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))

        self.assertEqual( mgr.list_clusters()[0][0], 'testeminvm' )

        c.destroy_files_only()

    def testClusterFilesEMinVMpm1(self):
        '''Test cluster with EM present'''
        #print '++++++++++ DEBUG: starting testClusterFilesEMinVM'
        mgr = ClusterMgr()

        s = """{
            "name" : "em-cluster",
            "idbversion" : "4.5.0-1", 
            "binary" : true,
            "boxtype" : "cal-precise64",
            "em" : { "present" : true, "invm" : true, "role" : "pm1" },
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "memory" : 1024,
                    "dbroots_per" : 1
                }
              }
            }
            """
        cfg = ConfigSpec(s)

        c = mgr.alloc_new('testeminvmpm1',cfg,'vagrant')
        ref_file = '%s/testeminvmpm1-Vagrantfile' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, c._vmi._vfile))

        self.assertEqual( mgr.list_clusters()[0][0], 'testeminvmpm1' )

        c.destroy_files_only()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
