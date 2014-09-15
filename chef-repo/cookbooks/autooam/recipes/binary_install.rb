if "#{node[:idbuser]}" == "root"
  homedir = "/root"
  tardir = "/usr/local"
  idbinstalldir = "/usr/local/Calpont"
  password = "qalpont!"
else
  homedir = "/home/#{node[:idbuser]}"
  tardir = "#{homedir}"
  idbinstalldir = "/home/#{node[:idbuser]}/Calpont"  
  password = "infinidb"
end

template "/#{homedir}/dobinaryinstall.sh" do
  source "dobinaryinstall.erb"
  mode 0755
  owner "#{node[:idbuser]}"
  group "#{node[:idbuser]}"
  variables({
    :idbuser => "#{node[:idbuser]}",
    :idbinstalldir => "#{idbinstalldir}",
    :homedir => "#{homedir}",
    :pkgfile => "#{node[:pkgfile]}",
    :tardir => "#{tardir}"
  })
end

bash "install_idb" do
  user "#{node[:idbuser]}"
  cwd "#{homedir}"
  code <<-EOH
  ./dobinaryinstall.sh 
  EOH
end

if node[:hadoopenv].nil?

  template "/#{homedir}/runpostconfigure.sh" do
    source "runpostconfigure.erb"
    mode 0755
    owner "#{node[:idbuser]}"
    group "#{node[:idbuser]}"
    variables({
      :idbuser => "#{node[:idbuser]}",
      :idbuserpasswd => "#{password}",
      :idbinstalldir => "#{idbinstalldir}",
      :postconfig_opts => "#{node[:postconfig_opts]}"
    })
  end

else

  template "/#{homedir}/runpostconfigure.sh" do
    source "runpostconfigure_hadoop.erb"
    mode 0755
    owner "#{node[:idbuser]}"
    group "#{node[:idbuser]}"
    variables({
      :idbuser => "#{node[:idbuser]}",
      :idbuserpasswd => "#{password}",
      :idbinstalldir => "#{idbinstalldir}",
      :hadoopenv => "#{node[:hadoopenv]}",
      :postconfig_opts => "#{node[:postconfig_opts]}"
    })
  end

end

if node[:pkgversion][0,1] >= "4"

  node[:machines].each do |mach|
    bash "install_healthcheck_remote" do
      user "#{node[:idbuser]}"
      cwd "#{homedir}"
      code <<-EOH
      scp /packages/#{node[:pkgversion]}/packages/Calpont/bin/healthcheck #{mach[:ip]}:.
      EOH
    end
  end

else

  node[:machines].each do |mach|
    bash "install_healthcheck_remote" do
      user "#{node[:idbuser]}"
      cwd "#{homedir}"
      code <<-EOH
      ssh #{mach[:ip]} 'ln -s #{idbinstalldir}/bin/healthcheck .'
      EOH
    end
  end

end

bash "runpostconfigure" do
  user "root"
  cwd "#{homedir}"
  code <<-EOH
  ./runpostconfigure.sh 
  EOH
end

