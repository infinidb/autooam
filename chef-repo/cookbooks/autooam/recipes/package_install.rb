bash "install_idb" do
  user "root"
  cwd "/root"
  code <<-EOH
  tar -zxf "/packages/#{node[:pkgfile]}"
  EOH
end

pkgpatt = "calpont"
if node[:pkgversion][0,1] >= "4"
  pkgpatt = "infinidb"
  end

case node[:platform_family]
  when "debian"

    bash "install_pkgs" do
      user "root"
      cwd "/root"
      code <<-EOH
      dpkg -i #{pkgpatt}*.deb
      EOH
    end

  when "rhel"

    bash "install_pkgs" do
      user "root"
      cwd "/root"
      code <<-EOH
      rpm -i #{pkgpatt}*.rpm
      EOH
    end

end

if node[:hadoopenv].nil?

  template "/root/runpostconfigure.sh" do
    source "runpostconfigure.erb"
    mode 0755
    owner "root"
    group "root"
    variables({
      :idbuser => "root",
      :idbuserpasswd => "qalpont!",
      :idbinstalldir => "/usr/local/Calpont",
      :postconfig_opts => "#{node[:postconfig_opts]}"
    })
  end

else

  template "/root/runpostconfigure.sh" do
    source "runpostconfigure_hadoop.erb"
    mode 0755
    owner "root"
    group "root"
    variables({
      :idbuser => "root",
      :idbuserpasswd => "qalpont!",
      :idbinstalldir => "/usr/local/Calpont",
      :hadoopenv => "#{node[:hadoopenv]}",
      :postconfig_opts => "#{node[:postconfig_opts]}"
    })
  end

end

if node[:pkgversion][0,1] >= "4"

  node[:machines].each do |mach|
    bash "install_healthcheck_remote" do
      user "root"
      cwd "/root"
      code <<-EOH
      scp /packages/#{node[:pkgversion]}/packages/Calpont/bin/healthcheck #{mach[:ip]}:.
      EOH
    end
  end

else

  node[:machines].each do |mach|
    bash "install_healthcheck_remote" do
      user "root"
      cwd "/root"
      code <<-EOH
      ssh #{mach[:ip]} 'ln -s /usr/local/Calpont/bin/healthcheck .'
      EOH
    end
  end

end

bash "runpostconfigure" do
  user "root"
  cwd "/root"
  code <<-EOH
  /root/runpostconfigure.sh 
  EOH
end
