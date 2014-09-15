if "#{node[:idbuser]}" == "root"
  homedir = "/root"
  idbinstalldir = "/usr/local/Calpont"
else
  homedir = "/home/#{node[:idbuser]}"
  idbinstalldir = "/home/#{node[:idbuser]}/Calpont"  
end

if "#{node[:idbuser]}" != "root"
  directory "/var/log" do
    owner "root"
    group "root"
    mode 00777
    action :create
  end
end

template "/etc/default/infinidb" do
  source "infinidbdef.erb"
  mode 0755
  owner "root"
  group "root"
  variables({
    :idbinstalldir => "#{idbinstalldir}"
  })
end

template "/#{homedir}/updaterclocal.sh" do
  source "updaterclocal.erb"
  mode 0755
  owner "#{node[:idbuser]}"
  group "#{node[:idbuser]}"
  variables({
    :idbuser => "#{node[:idbuser]}",
    :idbinstalldir => "#{idbinstalldir}"
  })
end

bash "updaterclocal" do
  user "root"
  cwd "#{homedir}"
  code <<-EOH
  ./updaterclocal.sh 
  EOH
end
