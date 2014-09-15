autooam Installation
====================

This page covers the installation of autooam.  There are two modes for autooam to operate in - development mode and execution mode.  In development mode you will be able to run the autooam unit tests but not do anything that requires real VMs.  You can use development mode within a VM or on a "real" system. Execution mode is a superset of development mode and requires a "real" Linux os and the ability to launch vms.

This page will cover both modes - development mode first, then following on to execution mode.

Dependencies
------------

autooam requires the following:

* Python 2.7
* subversion
* make

Note that the Python version dependency creates an interesting challenge on CentOS as it bundles Python 2.6 as the "system" Python.  This is not insurmountable, but you will have to do some extra work to install a parallel version of Python 2.7 and then use Python virtualenv capability to reference the newer version when running autooam.  If you decide to go down this path, this page has a good set of instructions:

[Install Python 2.7.3 on Centos 6.2](http://toomuchdata.com/2012/06/25/how-to-install-python-2-7-3-on-centos-6-2/)

When you get to Python module installs below, make sure that you install to your 2.7 copy.

In any case, the remainder of this page is targeting an Ubuntu 12.04 install.  The CentOS install is somewhat more involved, both because of the Python issue and because of the packaging discontinuity inherent in CentOS (standard, EPEL, RPMForge, etc.).

Step 1: Create calpont user account
-----------------------------------

Create the calpont user working directory with IDs of 1100.

    adduser calpont --uid 1100 


Step 2: Check out autooam
-------------------------

Choose your working directory (I usually prefer a sub-directory of $HOME/workspace), then clone the git repo.

    cd workspace
    git clone git@srvengcm1.calpont.com:/repos/autooam

Step 3: Install Python packages
-------------------------------

autooam requires a few Python packages from the Python Package Index.  Install these as follows.

First, make sure the pip installer is installed on your system.

    sudo apt-get install python-pip

You will need some dependent packages to successfully install the MySQL Python library:

    sudo apt-get install python-dev libmysqlclient-dev

Now, install the packages.

    sudo pip install pymongo
    sudo pip install jprops
    sudo pip install MySQL-python
    sudo pip install psutil

NOTE: you can safely ignore the gcc related errors when installing pymongo - you don't need the natively compiled extensions for autooam.  Also, the attempt to install MySQL-python may error out and request an upgrade to the distribute package - just follow the instructions if it does.

Step 4: Install MongoDB
-----------------------

Technically this is an optional step as long as you know of a mongodb instance you can point to somewhere, but it is preferable to use a local instance.  The MongoDB download site is 
[here](http://www.mongodb.org/downloads).

This site had a nice set of instructions that I used for installation on Ubuntu: 

[How to install MongoDB on Ubuntu 12.04](https://www.digitalocean.com/community/articles/how-to-install-mongodb-on-ubuntu-12-04)

Note that if you do choose a non-local MongoDB install or anything non-standard, you will need to set these properties appropriately in your $AUTOOAM_HOME/conf/site.conf file:

    common.oammongo.dbhost = 'localhost'
    common.oammongo.dbport = 27017        
    common.oammongo.dbname = 'autooamdb'         

Step 5: Set AUTOOAM_HOME
------------------------

You need to set up a few environment variables so that python can find our autooam packages.  Set this is your .bashrc file:

    echo 'export AUTOOAM_HOME=<path-to-where-you-checked-out-autooam>/autooam' >> .bashrc
    echo 'export PYTHONPATH=$AUTOOAM_HOME:$PYTHONPATH' >> .bashrc

Step 6: Run the unit tests
--------------------------

At this point, you should be able to successfully run the autooam unit tests.  Just cd to your autooam directory and run 'make'.  There will be quite a bit of log output that is extraneous - look for the 'OK' at the end of the output to know that everything worked.

	$ cd $AUTOOAM_HOME
	$ make
	..
	----------------------------------------------------------------------
	Ran 35 tests in 1.243s
	
	OK

//**NOTE: if you are installing development mode only Stop here!**//

Step 7: Install virtualbox
--------------------------

The VirtualBox download site is [here](https://www.virtualbox.org/wiki/Downloads).

Depending on your OS, you may be able to install from standard repos (i.e. apt-get install virtualbox).  autooam is known to work with virtualbox 4.2.4 on ubuntu.  Other platforms/versions have not been tested.

For Ubuntu, followed these.  First add repo to /etc/apt/sources.list: 

    deb http://download.virtualbox.org/virtualbox/debian precise contrib

Then, register the key:

    wget -q http://download.virtualbox.org/virtualbox/debian/oracle_vbox.asc -O- | sudo apt-key add -

and install...

    sudo apt-get update
    sudo apt-get install virtualbox-4.2

Step 8: Install vagrant
-----------------------

The Vagrant download site is [here](http://downloads.vagrantup.com/).

Depending on your OS, you may be able to install from standard repos (i.e. apt-get install vagrant).
autooam is known to work with Vagrant 1.0.5 on ubuntu.  Other platforms/versions have not been tested.

For Ubuntu, download the 1.0.6 deb package from the download site, then install

    dpkg -i vagrant_x86_64.deb

Check to make sure that vagrant is now in your path.  In some older vagrant versions, you may have to add manually in .bashrc (see below)

    $ which vagrant
    /usr/bin/vagrant

If `which` fails then add vagrant to your path:

    echo "export PATH=$PATH:/opt/vagrant/bin" >> ~/.bashrc
    source ~/.bashrc

Step 9: Install vagrant boxes
-----------------------------

autooam uses a specific set of vagrant base boxes for testing.  For any new setup, these need to be added to your local vagrant install.  Note that depending on where you run this it may take quite awhile.  Each box is several hundred MB that has to be transferred from srvengcm1.

    $ python setup.py

Step 10: Package area configuration
-----------------------------------

To be able to run the framework you need to configure a package area.  The easiest way to do this is to mount the main InfiniDB package area on the host machine.  The alternative is to manually copy over the desired InfiniDB packages to a local area and keep this in sync over time.  For the purposes of this page, it is assumed you will mount the main package area.

First, make sure you have cifs-utils installed

    sudo apt-get install cifs-utils

Then, add the following line to your /etc/fstab and issue a 'mount -a':

    sudo mkdir /media/packages
    sudo bash -c "echo '//calweb/shared  /media/packages  cifs  username=oamuser,password=Calpont1  0  0' >> /etc/fstab"
    sudo mount -a

There are two relevant configuration properties for packages to be aware of although the default values are sufficient if these instructions are followed.

    vmi.versionmgr.basedir = '/media/packages/Iterations'
    vmi.versionmgr.packagedir' = '%s/examples' % (os.environ['AUTOOAM_HOME'])

The vmi.versionmgr.basedir property is intended to be a reference to the package build area.  If you mount the package build area any place other than /media/packages then you should change this property in your conf/site.properties file. This directory is not required to exist at all ��� it simply means that the framework will only look under vmi.versionmgr.packagedir for packages.  vmi.versionmgr.packagedir should always be a path that exists locally on the machine.  

In a normally configured environment, with xxx.basedir pointing to the package build area, the framework will always look for a version in both areas (reference/build area and local area).  If it finds a copy locally in xxx.packagedir it checks it against the reference/build area and if the local copy is out of date it will be updated.  If it is not found locally, then the framework will make a local copy the first time a version is used.  In this manner the framework provides efficient access to any package version that exists in the main InfiniDB package area.  

Step 11: NFS export configuration
---------------------------------

The framework assumes the ability to mount the AUTOOAM_HOME directory from the cluster VMs so you need to have nfs installed and an export configured.

First you will need NFS installed on your host.  On Ubuntu:

    sudo apt-get install nfs-kernel-server 

Assuming that is successful, you just need to add an entry to /etc/exports for your AUTOOAM_HOME:

    sudo bash -c "echo '<your AUTOOAM_HOME path> 192.168.0.0/255.255.0.0(rw,sync,no_subtree_check,anonuid=1100,anongid=1100)' >> /etc/exports"
    sudo exportfs -a

Note that if you have forgotten to do this, the framework checks prior to attempting to fire up a cluster and will error out with the steps that need to be performed.

Step 12: Cron job configuration
-------------------------------

Make sure any cron job file that is setup has the user of calpont:crontab.
Here is an example

    sudo chown calpont:crontab /var/spool/cron/crontabs/calpont

Step 13: mail setup

The autooam framework sends a summary email by default whenever a TestManager controlled run occurs (as in the autorun.py utility).  To enable this capability, a mail MTA must be configured on the system.  Follow these steps for install onto an Ubuntu host:

    sudo apt-get install exim4-daemon-light mailutils
    sudo dpkg-reconfigure exim4-config

For the initial menu select 'Mail sent by smarthost; no local mail'.  Then, take most default settings except for the domain (calpont.com) and the outgoing smarthost (srvemail1.calpont.com).

You can test to make sure that the configuration was successful with a command like:

    echo 'test' | mail -s test <your email id>@calpont.com

