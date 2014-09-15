bash "upgrade_idb" do
  user "root"
  cwd "/root"
  code <<-EOH
  tar -zxf "/packages/#{node[:upgfile]}"
  EOH
end

idbuserpasswd = "qalpont!"
idbinstalldir = "/usr/local/Calpont"

prevpatt = "calpont"
if node[:pkgversion][0,1] >= "4"
  prevpatt = "infinidb"
  end

newpatt = "calpont"
if node[:upgversion][0,1] >= "4"
  newpatt = "infinidb"
  end

case node[:platform_family]
  when "debian"
    bash "upgrade_debs" do
      user "root"
      cwd "/root"
      code <<-EOH
      mv #{idbinstalldir}/etc/Calpont.xml #{idbinstalldir}/etc/Calpont.xml.rpmsave
      dpkg-query -W -f '${package}\\n' | grep #{prevpatt} | xargs dpkg -P
      dpkg -i #{newpatt}*#{node[:upgversion]}*.deb
      EOH
    end

  when "rhel"
    bash "upgrade_rpms" do
      user "root"
      cwd "/root"
      code <<-EOH
      rpm -qa | grep #{prevpatt} | xargs rpm -e
      rpm -i #{newpatt}*#{node[:upgversion]}*.rpm
      EOH
    end
end

bash "fixup_calpontxml" do
  user "root"
  cwd "/root"
  code <<-EOH
  sed -i 's/<DBRootStorageType>local<\\/DBRootStorageType>/<DBRootStorageType>internal<\\/DBRootStorageType>/' #{idbinstalldir}/etc/Calpont.xml.rpmsave
  EOH
end

bash "runpostconfigure_upgrade" do
  user "root"
  cwd "/root"
  code <<-EOH
  #{idbinstalldir}/bin/postConfigure -p '#{idbuserpasswd}' -n -c #{idbinstalldir}/etc/Calpont.xml.rpmsave
  EOH
end
