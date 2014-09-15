Vagrant Boxes for autooam
=========================

Vagrant works against the concept of boxes.  A vagrant box is simply a virtual machine image with a base set of software that Vagrant can interact with for provisioning, communication, etc.

In the context of autooam, there needs to be a base Vagrant box for each OS platform to be supported and tested.  The philosophy behind the creation of base boxes is to have all required dependent software installed, but none of the configuration performed.  This has a few advantages:
  * The tests are not dependent on the presence nor speed of an external network connection that would be required if new software is installed
  * By keeping all configuration as part of an orchestration framework, everything is entirely repeatable and no steps are hidden

autooam depends on a set of boxes that correspond to boxes defined in the autooam.testlib.vagboxes module and must exist in the local vagrant install (the autooam setup utility performs the necessary vagrant box add).

autooam box creation and update
-------------------------------

autooam boxes are created from infrastructure that is part of the autooam repo in the autooam/vagrant subdirectory.

This directory consists of the following:

* Box subdirectories - each subdirectory of the vagrant directory represents a box type.  A valid box directory must contain a file name "VagrantFile" and on checkout this will be the only file in each directory.
* Ansible playbook - There is an ansible playbook (makebox.yml) and supporting files (inventory file, 'inventory', Ansible config file - 'ansible.cfg', and jdk tarball - 'jdk-7u55-linux-x64.gz').  This is a self-contained playbook that assumes a "stock" install and then configures the box for autooam.  The playbook is idempotent - i.e. can run repeatedly and always yield the same output.
* makebox.py - Python script to drive box creation.

The usage of makebox.py is as follows:

	usage: usage: makebox.py [-hlrb:d]
	    
	    Options:
	        -h        : show usage
	        -l        : install new boxes locally
	        -r        : install new boxes remote
	        -b <box>  : process a singe named box (default = all subdirectories) 
	        -d        : destroy box and start over (defaut = use existing box state)
	        
	    basebox : initial box - can be remote or local
	    boxname : new box to create

So, for example, if you want to create all boxes and install locally, you would run this:

    ./makebox.py -l

Note that this will take awhile the first time you run it.  The time consuming portions are:

* Downloading the initial box - the initial has to be downloaded from the web
* Dependency additions - after the box is up there are several dependencies that have to be installed
* .box file creation - we have to write out the box to a new .box file after each run.

Subsequent runs will be significantly faster since the first 2 steps will take virtually no time.

Updating boxes
--------------

If you need to update a box, the proper procedure is as follaws:
  * Updated the makebox.yml Ansible playbook as needed
  * Run makebox.py -l
  * Test changes locally
  * RUn makebox.py -r to update the box repo on srvengcm1
  * Rerun setup.py on each autooam machine

Adding a box
------------

To add a box, the steps are as follows:
  * Create a new cal-xxx subdirectory the autooam vagrant/ directory
  * From the directory do `vagrant init <base box URL>` - this creates the initial VagrantFile
  * git add VagrantFile (for future commit to repo)
  * Run makebox.py -b <boxname> -l to create the new box and install locally
  * Update autooam.testlib.vagboxes as appropriate for the new box (see details below this list)
  * Test changes locally
  * RUn makebox.py -b <boxname> -r to update the box repo on srvengcm1
  * Rerun setup.py on each autooam machine

To add a new box in autooam/testlib/vagboxes.py, add a new entry to the register map of the form:

    'box name' : ('<version description>', '<default package-type>', '<os-family>', '<os-version>')

For example, see the new entry added at the end for CentOS 5.8.

	register = {
	    'cal-precise64' : ('Ubuntu 12.04.1 LTS (Precise Pangolin)','deb', 'ubuntu', '12.04'),
	    'cal-lucid64' : ('Ubuntu 10.04.4 LTS (Lucid Lynx)','deb', 'ubuntu', '10.04'),
	    'cal-centos58' : ('CentOS release 5.8 (Final)','rpm', 'centos', '5.8')
	}

