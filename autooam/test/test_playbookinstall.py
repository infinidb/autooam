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
Created on Feb 28, 2014

@author: Damon Cathey
'''
import unittest
from autooam.cluster.cluster import Cluster
from emtools.cluster.configspec import ConfigSpec
from autooam.cluster.clustermgr import ClusterMgr
from emtools.cluster.playbookinstall import PlaybookInstall
import json
import test_common
import emtools.common.utils as utils

def mysyscb(cmd):
    return (0,"","")

class PlaybookInstallTest(unittest.TestCase):

    def setUp(self):
        # need to disable real system calls for unit-test
        utils.syscall_cb = mysyscb

    def tearDown(self):
        pass

    def testConstruct(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testConstruct'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "4.0",
            "binary" : true,
            "boxtype" : "cal-centos6",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """

        cfg = ConfigSpec(s)
        c = Cluster('aClusterName', cfg, 'a-cluster')
        with self.assertRaisesRegexp(Exception,"Invalid cluster ansible playbook installer type"):
            p = PlaybookInstall(c, 'bogus-optype')
        p1 = PlaybookInstall(c, 'pkginstall')
        p2 = PlaybookInstall(c, 'pkgupgrade')
        p3 = PlaybookInstall(c, 'bininstall')
        p4 = PlaybookInstall(c, 'binupgrade')

    def testRPMInstall_3(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testRPMInstall_3'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "3.5.1-5",
            "boxtype" : "cal-centos6",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('rpmInstallCluster_3',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testRPMInstall_4(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testRPMInstall_4'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "4.0.0-0",
            "boxtype" : "cal-centos6",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('rpmInstallCluster_4',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testRPMInstallHadoop_4(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testRPMInstallHadoop_4'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "4.0.0-0",
            "boxtype" : "cal-centos6",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1,
                    "memory" : 8192
                    },
                "um" : {
                    "count" : 1,
                    "memory" : 8192
                    }
                },
            "hadoop" : {
                "instance-templates" : "2 hadoop-datanode+hadoop-tasktracker,1 hadoop-namenode+hadoop-jobtracker",
                "templates-namenode" : "um1",
                "templates-datanode" : "pm1+pm2"
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('rpmInstallHadoopCluster_4',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testRPMUpgrade(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testRPMUpgrade'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "3.5.1-5",
            "upgrade" : "4.0.0-0",
            "boxtype" : "cal-centos6",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('rpmUpgradeCluster',cfg,'vagrant',False)
        c.run_upgrade_recipe()

        c.destroy_files_only()

    def testDEBInstall_3(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testDEBInstall_3'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "3.5.1-5",
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('debInstallCluster_3',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testDEBInstall_4(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testDEBInstall_4'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "4.0.0-0",
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('debInstallCluster_4',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testDEBInstallHadoop_4(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testDEBInstallHadoop_4'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "4.0.0-0",
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1,
                    "memory" : 8192
                    },
                "um" : {
                    "count" : 1,
                    "memory" : 8192
                    }
                },
            "hadoop" : {
                "instance-templates" : "2 hadoop-datanode+hadoop-tasktracker,1 hadoop-namenode+hadoop-jobtracker",
                "templates-namenode" : "um1",
                "templates-datanode" : "pm1+pm2"
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('debInstallHadoopCluster_4',cfg,'vagrant',False)
        c.run_install_recipe()
 
        c.destroy_files_only()

    def testDEBUpgrade(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testDEBUpgrade'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "3.5.1-5",
            "upgrade" : "4.0.0-0",
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('debUpgradeCluster',cfg,'vagrant',False)
        c.run_upgrade_recipe()

        c.destroy_files_only()

    def testBinInstall_3(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testBinInstall_3'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "3.5.1-5",
            "boxtype" : "cal-centos6",
            "binary" : true,
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('binInstallCluster_3',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testBinInstall_4(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testBinInstall_4'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "4.0",
            "boxtype" : "cal-centos6",
            "binary" : true,
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('binInstallCluster_4',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testBinInstallHadoop_4(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testBinInstallHadoop_4'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "4.0",
            "boxtype" : "cal-centos6",
            "binary" : true,
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                },
            "hadoop" : {
                "instance-templates" : "2 hadoop-datanode+hadoop-tasktracker,1 hadoop-namenode+hadoop-jobtracker",
                "templates-namenode" : "um1",
                "templates-datanode" : "pm1+pm2"
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('binInstallClusterHadoop_4',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testBinUpgrade(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testBinUpgrade'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "3.5.1-5",
            "upgrade" : "4.0",
            "boxtype" : "cal-centos6",
            "binary" : true,
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('binUpgradeCluster',cfg,'vagrant',False)
        c.run_upgrade_recipe()

        c.destroy_files_only()

    def testBinInstallNonRoot_4(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testBinInstallNonRoot_4'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "4.0",
            "boxtype" : "cal-centos6",
            "binary" : true,
            "nonrootuser" : true,
            "idbuser" : "calpont",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('binInstallCluster_4',cfg,'vagrant',False)
        c.run_install_recipe()

        c.destroy_files_only()

    def testBinUpgradeNonRoot(self):
        #print '++++++++++ DEBUG: starting PlaybookInstallTest testBinUpgradeNonRoot'
        s = """{
            "name" : "1um_2pm",
            "idbversion" : "3.5.1-5",
            "upgrade" : "4.0",
            "boxtype" : "cal-centos6",
            "binary" : true,
            "nonrootuser" : true,
            "idbuser" : "calpont",
            "rolespec" : {
                "pm" : {
                    "count" : 2,
                    "dbroots_per" : 1
                    },
                "um" : {
                    "count" : 1
                    }
                }
            }
            """
        mgr = ClusterMgr()
        cfg = ConfigSpec(s)
        c   = mgr.alloc_new('binUpgradeCluster',cfg,'vagrant',False)
        c.run_upgrade_recipe()

        c.destroy_files_only()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
