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
Created on Dec 17, 2012

@author: rtw
'''
import unittest
import test_common
import os
import getpass
from emtools.cluster.configspec import ConfigSpec
import emtools.common as common

class TestConfigSpec(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testNegative1(self):
        '''test malformed json as well as non-map root objects'''
        with self.assertRaisesRegexp(ValueError,"Extra data.*"):        
            ConfigSpec('"key" : "value"')
        with self.assertRaisesRegexp(Exception,".*not a map.*"):        
            ConfigSpec('["key", "value"]')
            ConfigSpec('"somevalue"')
        with self.assertRaisesRegexp(ValueError,"Expecting.*"):        
            ConfigSpec('["key" : "value"')

    def testNegative2(self):
        '''test missing idbversion'''
        s = """{
            "name" : "a-cluster", 
            "boxtype" : "cal-precise64",
            "rolespec" : {}
            }
            """
        with self.assertRaisesRegexp(Exception,"ConfigSpec did not specify.*idbversion"):        
            ConfigSpec(s)
            
    def testNegative3(self):
        '''test missing name'''
        s = """{
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {}
            }
            """
        with self.assertRaisesRegexp(Exception,"ConfigSpec did not specify.*name"):        
            ConfigSpec(s)

    def testNegative5(self):
        '''test missing rolespec'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64"
            }
            """
        with self.assertRaisesRegexp(Exception,"ConfigSpec did not specify.*rolespec"):        
            ConfigSpec(s)

    def testNegative6(self):
        '''test a wrong type for machines'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : "myrolespecs"
            }
            """
        with self.assertRaisesRegexp(Exception,"ConfigSpec has wrong type.*rolespec"):        
            ConfigSpec(s)

    def testNegative7(self):
        '''Test missing pm rolespec'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                    }
                }
            }
            """
        with self.assertRaisesRegexp(Exception,"rolespec does not specify a pm role.*"):        
            ConfigSpec(s)

    def testNegative8(self):
        '''Test missing count in pm role'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "dbroots_per" : 1
                    }
                }
            }
            """
        with self.assertRaisesRegexp(Exception,"ConfigSpec did not specify required attribute.*count"):        
            ConfigSpec(s)

    def testNegative9(self):
        '''Test missing dbroots_* in pm role'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 1
                    }
                }
            }
            """
        with self.assertRaisesRegexp(Exception,"Must specify either dbroots_per or dbroots_list.*"):        
            ConfigSpec(s)

    def testNegative10(self):
        '''Test multiple dbroots_* in pm role'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 1,
                    "dbroots_per" : 4,
                    "dbroots_list" : [[1,2,3,4]]
                    }
                }
            }
            """
        with self.assertRaisesRegexp(Exception,"Cannot specify both dbroots_.*"):        
            ConfigSpec(s)

    def testNegative11(self):
        '''Test invalid dbroots_per'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 1,
                    "dbroots_per" : 0
                    }
                }
            }
            """
        with self.assertRaisesRegexp(Exception,"Must have at least 1 dbroot per pm.*"):        
            ConfigSpec(s)

    def testNegative12(self):
        '''Test invalid dbroots_per'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 1,
                    "dbroots_list" : [1,2,3,4]
                    }
                }
            }
            """
        with self.assertRaisesRegexp(Exception,"Length of dbroots_list must match pm count.*"):        
            ConfigSpec(s)

    def testNegative13(self):
        '''Test invalid dbroots_per'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 1,
                    "dbroots_list" : [1]
                    }
                }
            }
            """
        with self.assertRaisesRegexp(Exception,"dbroots_list.* is not a list.*"):        
            ConfigSpec(s)
            
    def testNegative14(self):
        '''Test invalid dbroots_per'''
        s = """{
            "name" : "a-cluster", 
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 1,
                    "dbroots_per" : 8
                    },
                "um" : {
                    "count" : 1
                    },
                "umpm" : {
                    "count" : 1
                    }                    
                }
            }
            """
        with self.assertRaisesRegexp(Exception,"Unknown role.*"):        
            ConfigSpec(s)

    def testUpdate(self):
        s = """{
            "name" : "b-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_list" : [[1,2],[3,4],[5,6],[7,8]]
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        cfg['newattr'] = 'newvalue'
        self.assertEqual( cfg['newattr'], "newvalue" )
            
    def testConstruct1(self):
        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertEqual( cfg['name'], "a-cluster" )
        self.assertEqual( cfg['idbversion'], "3.5.1-4" )
        self.assertEqual( cfg['boxtype'], "cal-precise64" )
        self.assertEqual( len(cfg['rolespec']), 2 )
        self.assertEqual( cfg['rolespec']['pm']['count'] , 4 )
        self.assertEqual( cfg['rolespec']['pm']['memory'] , 1024 )
        self.assertEqual( cfg['rolespec']['pm']['dbroots_per'] , 2 )
        self.assertEqual( cfg['rolespec']['um']['count'] , 1 )
        self.assertEqual( cfg['rolespec']['um']['memory'] , 1024 )

    def testConstruct2(self):
        s = """{
            "name" : "b-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_list" : [[1,2],[3,4],[5,6],[7,8]]
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertEqual( cfg['name'], "b-cluster" )
        self.assertEqual( cfg['idbversion'], "3.5.1-4" )
        self.assertEqual( cfg['boxtype'], "cal-precise64" )
        self.assertEqual( len(cfg['rolespec']), 1 )
        self.assertEqual( cfg['rolespec']['pm']['count'] , 4 )
        self.assertEqual( cfg['rolespec']['pm']['memory'] , 1024 )
        self.assertEqual( len(cfg['rolespec']['pm']['dbroots_list']) , 4 )
        self.assertEqual( len(cfg['rolespec']['pm']['dbroots_list'][0]) , 2 )
        self.assertEqual( cfg['rolespec']['pm']['dbroots_list'][0][0] , 1 )
        self.assertEqual( cfg['rolespec']['pm']['dbroots_list'][0][1] , 2 )

    def testConstructFromFile(self):
        cspecfile = '/tmp/%s_cspec' % getpass.getuser()
        f = open(cspecfile,'w')
        s = """{
            "name" : "c-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_list" : [[1,2],[3,4],[5,6],[7,8]]
                }
              }
            }
            """
        f.write(s)
        f.close()
        
        cfg = ConfigSpec(jsonfile=cspecfile)
        self.assertEqual( cfg['name'], "c-cluster" )
        self.assertEqual( cfg['idbversion'], "3.5.1-4" )
        self.assertEqual( cfg['boxtype'], "cal-precise64" )
        self.assertEqual( len(cfg['rolespec']), 1 )
        self.assertEqual( cfg['rolespec']['pm']['count'] , 4 )
        self.assertEqual( cfg['rolespec']['pm']['memory'] , 1024 )
        self.assertEqual( len(cfg['rolespec']['pm']['dbroots_list']) , 4 )
        self.assertEqual( len(cfg['rolespec']['pm']['dbroots_list'][0]) , 2 )
        self.assertEqual( cfg['rolespec']['pm']['dbroots_list'][0][0] , 1 )
        self.assertEqual( cfg['rolespec']['pm']['dbroots_list'][0][1] , 2 )

        os.remove(cspecfile)

    def testConstructOverride(self):
        cspecfile = '/tmp/%s_cspec' % getpass.getuser()
        f = open(cspecfile,'w')
        s = """{
            "name" : "d-cluster",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_list" : [[1,2],[3,4],[5,6],[7,8]]
                }
              }
            }
            """
        f.write(s)
        f.close()
        
        cfg = ConfigSpec(jsonfile=cspecfile,idbversion='some-old-version',boxtype='some-old-boxtype')
        self.assertEqual( cfg['name'], "d-cluster" )
        self.assertEqual( cfg['idbversion'], "some-old-version" )
        self.assertEqual( cfg['boxtype'], "some-old-boxtype" )
        self.assertEqual( len(cfg['rolespec']), 1 )
        self.assertEqual( cfg['rolespec']['pm']['count'] , 4 )
        self.assertEqual( cfg['rolespec']['pm']['memory'] , 1024 )
        self.assertEqual( len(cfg['rolespec']['pm']['dbroots_list']) , 4 )
        self.assertEqual( len(cfg['rolespec']['pm']['dbroots_list'][0]) , 2 )
        self.assertEqual( cfg['rolespec']['pm']['dbroots_list'][0][0] , 1 )
        self.assertEqual( cfg['rolespec']['pm']['dbroots_list'][0][1] , 2 )

        os.remove(cspecfile)

    def testNonroot(self):
        # test the default value when not specified
        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('idbuser') )
        self.assertEqual( cfg['idbuser'], 'root' )
        self.assertEqual(cfg.infinidb_install_dir(), '/usr/local/Calpont')

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "idbuser" : "calpont",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('idbuser') )
        self.assertEqual( cfg['idbuser'], 'calpont' )
        self.assertEqual(cfg.infinidb_install_dir(), '/home/calpont/Calpont')

    def testDatdup(self):
        # test the default value when not specified
        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "idbuser" : "calpont",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('datdup') )
        self.assertFalse( cfg['datdup'] )

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "idbuser" : "calpont",
            "datdup"  : true,
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('datdup') )
        self.assertTrue( cfg['datdup'] )

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "idbuser" : "calpont",
            "datdup"  : "true",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        with self.assertRaisesRegexp(Exception,"ConfigSpec has wrong type for attribute datdup.*"):        
            cfg = ConfigSpec(s)

    def testVersionGT(self):
        self.assertTrue( ConfigSpec._version_greaterthan('3.5', '3.5.1-5'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5.1', '3.5.1-5'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.1.1-2', '3.5.1-5'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2-1', '3.5.1-5'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5', '2.2'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5', '4.0'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5', '3.0'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.0', '3.5'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5', '3.5'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5.1-5','3.5'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5.1','3.5.2'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2','3.5.1'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2','3.5.2'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2-1','3.5.2-1'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2-2','3.5.2-1'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5.2-2','3.5.2-3'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2.1-1','3.5.2.1-1'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2.1-2','3.5.2.1-1'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5.2.1-2','3.5.2.1-3'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2.1','3.5.2.0'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5.2.1','3.5.2.2'))
        self.assertTrue( ConfigSpec._version_greaterthan('3.5.2.1-1','3.5.2.1'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5.2.1','3.5.2.1-1'))
        self.assertTrue( ConfigSpec._version_greaterthan('Latest','3.5.2.1'))
        self.assertTrue( ConfigSpec._version_greaterthan('Latest','3.5'))
        self.assertTrue( ConfigSpec._version_greaterthan('Latest','4.0'))
        self.assertFalse( ConfigSpec._version_greaterthan('3.5','Latest'))
        self.assertFalse( ConfigSpec._version_greaterthan('2.2.7-2','2.2.10-1'))
        self.assertTrue( ConfigSpec._version_greaterthan('2.2.10-1','2.2.7-2'))
        self.assertTrue( ConfigSpec._version_greaterthan('4.0.0-1','4.0.0-0'))
        self.assertFalse( ConfigSpec._version_greaterthan('4.0.0-0','4.0.0-1'))
        self.assertTrue( ConfigSpec._version_greaterthan('4.0.0-1','4.0.0-1_old'))
        self.assertFalse( ConfigSpec._version_greaterthan('4.0.0-1_old','4.0.0-1'))

    def testSort(self):
        versions = ['1.0.6-1', '2.0.3.1-1', '2.0.4-1', '2.2', '2.2.10-1', '2.2.7-2']
        self.assertEqual(sorted(versions,cmp=ConfigSpec._version_cmp),['1.0.6-1', '2.0.3.1-1', '2.0.4-1', '2.2.7-2', '2.2.10-1', '2.2'])
         
    def testBinary(self):
        # test the default value when not specified
        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('binary') )
        self.assertFalse( cfg['binary'] )

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "binary"  : true,
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('binary') )
        self.assertTrue( cfg['binary'] )

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "binary"  : false,
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('binary') )
        self.assertFalse( cfg['binary'] )

        s = """{
            "name" : "a-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype" : "cal-precise64",
            "idbuser" : "calpont",
            "binary"  : "true",
            "rolespec" : {
                "pm" : {
                    "count" : 4,
                    "memory" : 1024,
                    "dbroots_per" : 2
                },
                "um" : {
                    "count" : 1,
                    "memory" : 1024
                }
              }
            }
            """
        with self.assertRaisesRegexp(Exception,"ConfigSpec has wrong type for attribute binary.*"):        
            cfg = ConfigSpec(s)

    def testExtstore(self):
        # test the default value when not specified
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
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
        self.assertTrue( cfg.has_key('storage') )
        self.assertEqual( cfg['storage'], 'internal' )

        # test with external storage enabled
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "storage"    : "external",
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
        self.assertTrue( cfg.has_key('storage') )
        self.assertEqual( cfg['storage'], 'external' )

        # test incorrect setting for external storage flag
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "storage"    : true,
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
        with self.assertRaisesRegexp(Exception,"ConfigSpec has wrong type for attribute storage.*"):
            cfg = ConfigSpec(s)

    def testUpgrade(self):
        # test the default value when not specified
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('upgrade') )
        self.assertEqual( cfg['upgrade'], '' )

        # test with external storage enabled
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "upgrade"    : "3.5.2-2",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('upgrade') )
        self.assertEqual( cfg['upgrade'], '3.5.2-2' )

    def testHadoop(self):
        # test a success path
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64-hadoop",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              },
            "hadoop"     : {
              "instance-templates" : "1 hadoop-namenode+hadoop-jobtracker,2 hadoop-datanode+hadoop-tasktracker"
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('hadoop') )
        self.assertEqual( cfg['hadoop']['instance-templates'], "1 hadoop-namenode+hadoop-jobtracker,2 hadoop-datanode+hadoop-tasktracker" )

        # Disabled this test.
        # Hadoop/boxtype validation now takes place in vagrantvmi to decouple
        # from configspec, which is now in emtools.
        # test invalid boxtype
        #s = """{
        #    "name"       : "e-cluster",
        #    "idbversion" : "3.5.1-4", 
        #    "boxtype"    : "cal-precise64",
        #    "upgrade"    : "3.5.2-2",
        #    "rolespec"   : {
        #        "pm" : {
        #            "count"       : 2,
        #            "memory"      : 1024,
        #            "dbroots_per" : 2
        #        }
        #      },
        #    "hadoop"     : {
        #      "instance-templates" : "1 hadoop-namenode+hadoop-jobtracker,2 hadoop-datanode+hadoop-tasktracker",
        #      "version" : "1.2.1"
        #      }
        #    }
        #    """
        #with self.assertRaisesRegexp(Exception,"Hadoop not supported on boxtype.*"):
        #    cfg = ConfigSpec(s)

    def testEnterprise(self):
        # test the default value when not specified
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('enterprise') )
        self.assertEqual( cfg['enterprise'], True )

        # test with enterprise specified
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "enterprise" : false,
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('enterprise') )
        self.assertEqual( cfg['enterprise'], False )

    def testMemUpdate(self):
        # test the default value when not specified
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertFalse( cfg['rolespec']['pm'].has_key('memory') )
        cfg['rolespec']['pm']['memory'] = 1024
        self.assertTrue( cfg['rolespec']['pm'].has_key('memory') )
        self.assertEquals( cfg['rolespec']['pm']['memory'], 1024 )
        cfg['rolespec']['pm']['memory'] = 4096
        self.assertEquals( cfg['rolespec']['pm']['memory'], 4096 )
         
    def testPmQuery(self):
        # test the default value when not specified
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('pm_query') )
        self.assertEqual( cfg['pm_query'], False )

        # test with enterprise specified
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "4.5.0-1", 
            "boxtype"    : "cal-precise64",
            "pm_query"   : true,
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('pm_query') )
        self.assertEqual( cfg['pm_query'], True )
        
        # now test an invalid config
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "pm_query"   : true,
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        with self.assertRaisesRegexp(Exception,"PM local query option only supported.*"):
            cfg.validate()
        
    def testEm(self):
        # test the default value when not specified
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('em') )
        self.assertEqual( cfg['em'], None )

        # test with em option
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "4.5.0-1", 
            "boxtype"    : "cal-precise64",
            "em"         : { "present" : true },
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('em') )
        self.assertEqual( cfg['em']['present'], True )
        self.assertEqual( cfg['em']['emhost'], 'localhost' )
        self.assertEqual( cfg['em']['emport'], 9090 )
        self.assertEqual( cfg['em']['oamserver_role'], 'um1' )
        self.assertEqual( cfg['em']['invm'], False )
        self.assertFalse( cfg['em'].has_key('boxtype') )
        self.assertFalse( cfg['em'].has_key('version') )

        # test with fully specified em option
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "4.5.0-1", 
            "boxtype"    : "cal-precise64",
            "em"         : { "present" : true, "emhost" : "testhost", "emport" : 7120, "oamserver_role" : "pm1" },
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        self.assertTrue( cfg.has_key('em') )
        self.assertEqual( cfg['em']['present'], True )
        self.assertEqual( cfg['em']['emhost'], 'testhost' )
        self.assertEqual( cfg['em']['emport'], 7120 )
        self.assertEqual( cfg['em']['oamserver_role'], 'pm1' )
        self.assertEqual( cfg['em']['invm'], False )
        
        # now test an invalid config
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "em"         : { "foo" : "bar" },
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        with self.assertRaisesRegexp(Exception,"Must specify present flag.*"):
            cfg = ConfigSpec(s)

        # now test an invalid config
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "em"         : { "present" : true },
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        cfg = ConfigSpec(s)
        with self.assertRaisesRegexp(Exception,"Enterprise Manager.*only supported.*"):
            cfg.validate()
            
        # test the whether the global empresent property works
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "4.5.0-1", 
            "boxtype"    : "cal-centos6",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        common.props['cluster.cluster.empresent'] = True
        try:
            cfg = ConfigSpec(s)
        except Exception, exc:
            common.props['cluster.cluster.empresent'] = False
            raise exc
        common.props['cluster.cluster.empresent'] = False
        self.assertTrue( cfg.has_key('em') )
        self.assertEqual( cfg['em']['present'], True )
        self.assertEqual( cfg['em']['emhost'], 'localhost' )
        self.assertEqual( cfg['em']['emport'], 9090 )
        self.assertEqual( cfg['em']['oamserver_role'], 'um1' )
        self.assertEqual( cfg['em']['invm'], False )

        # the global flag shouldn't do anything if the version
        # doesn't support the em
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "3.5.1-4", 
            "boxtype"    : "cal-precise64",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        common.props['cluster.cluster.empresent'] = True
        try:
            cfg = ConfigSpec(s)
        except Exception, exc:
            common.props['cluster.cluster.empresent'] = False
            raise exc
        common.props['cluster.cluster.empresent'] = False
        self.assertTrue( cfg.has_key('em') )
        self.assertEqual( cfg['em'], None )

        # test the whether the invm flag works as expected
        s = """{
            "name"       : "e-cluster",
            "idbversion" : "4.5.0-1", 
            "boxtype"    : "cal-centos6",
            "rolespec"   : {
                "pm" : {
                    "count"       : 2,
                    "memory"      : 1024,
                    "dbroots_per" : 2
                }
              }
            }
            """
        common.props['cluster.cluster.eminvm'] = True
        try:
            cfg = ConfigSpec(s)
        except Exception, exc:
            common.props['cluster.cluster.eminvm'] = False
            raise exc
        common.props['cluster.cluster.eminvm'] = False
        self.assertTrue( cfg.has_key('em') )
        self.assertEqual( cfg['em']['present'], True )
        self.assertEqual( cfg['em']['emhost'], 'localhost' )
        self.assertEqual( cfg['em']['emport'], 9090 )
        self.assertEqual( cfg['em']['oamserver_role'], 'um1' )
        self.assertEqual( cfg['em']['invm'], True )
        self.assertEqual( cfg['em']['boxtype'], 'cluster' )
        self.assertEqual( cfg['em']['version'], 'Latest' )

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
