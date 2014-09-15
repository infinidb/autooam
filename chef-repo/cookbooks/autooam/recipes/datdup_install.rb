if "#{node[:idbuser]}" == "root"
  homedir = "/root"
  tardir = "/usr/local"
  idbinstalldir = "/usr/local/Calpont"
else
  homedir = "/home/#{node[:idbuser]}"
  tardir = "#{homedir}"
  idbinstalldir = "/home/#{node[:idbuser]}/Calpont"  
end

case node[:platform]
  when "ubuntu"
    bash "glusterfs_install" do
      user "root"
      cwd "/root"
      code <<-EOH
      apt-get update
      apt-get install -y python-software-properties
      add-apt-repository -y ppa:semiosis/ubuntu-glusterfs-3.4
      apt-get update
      apt-get install -y glusterfs-server
      EOH
    end

  when "debian"
    if node[:platform_version][0,1] == "6" 
      bash "glusterfs_install" do
        user "root"
        cwd "/root"
        code <<-EOH
        wget -O - http://download.gluster.org/pub/gluster/glusterfs/3.3/3.3.1/Debian/gpg.key | apt-key add -
        echo 'deb http://download.gluster.org/pub/gluster/glusterfs/3.3/3.3.1/Debian/squeeze.repo squeeze main' > /etc/apt/sources.list.d/gluster.list 
        apt-get update
        apt-get install -y glusterfs-server
        EOH
      end
    elsif node[:platform_version][0,1] == "7"
      bash "glusterfs_install" do
        user "root"
        cwd "/root"
        code <<-EOH
        wget -O - http://download.gluster.org/pub/gluster/glusterfs/3.4/3.4.3/Debian/pubkey.gpg | apt-key add -
        echo deb http://download.gluster.org/pub/gluster/glusterfs/3.4/3.4.3/Debian/apt wheezy main > /etc/apt/sources.list.d/gluster.list 
        apt-get update
        apt-get install -y glusterfs-server
        EOH
      end
    end

  when "centos"
    bash "glusterfs_install" do
      user "root"
      cwd "/root"
      code <<-EOH
      wget -P /etc/yum.repos.d http://download.gluster.org/pub/gluster/glusterfs/LATEST/EPEL.repo/glusterfs-epel.repo
      yum install -y glusterfs-server glusterfs-fuse
      service glusterd start
      chkconfig glusterd on
      EOH
    end

end
