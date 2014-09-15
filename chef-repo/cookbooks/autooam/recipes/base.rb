include_recipe 'hostsfile'

node[:machines].each do |mach|
  hostsfile_entry mach[:ip] do
    hostname mach[:hostname]
    aliases ["#{mach[:role]}"]
    action :create_if_missing
  end
end

template "/root/mountautooam.sh" do
  source "mountautooam.erb"
  mode 0755
  owner "root"
  group "root"
  variables({
    :hostip => "#{node[:hostip]}",
    :autooam_home => "#{node[:autooam_home]}",
    :idbuser => "#{node[:idbuser]}"
  })
end

bash "mountautooam" do
  user "root"
  cwd "/root"
  code <<-EOH
  ./mountautooam.sh 
  EOH
end

if "#{node[:idbuser]}" == "root"
  idbinstalldir = "/usr/local/Calpont"
else
  idbinstalldir = "/home/#{node[:idbuser]}/Calpont"  
end

template "/root/mountdbroots.sh" do
  source "mountdbroots.erb"
  mode 0755
  owner "root"
  group "root"
  variables({
    :dbroot_storage_type => "#{node[:dbroot_storage_type]}",
    :dbroot_count => "#{node[:dbroot_count]}",
    :remote_dbroot_basedir => "#{node[:remote_dbroot_basedir]}",
    :idbuser => "#{node[:idbuser]}",
    :idbinstalldir => "#{idbinstalldir}",
  })
end

bash "mountdbroots" do
  user "root"
  cwd "/root"
  code <<-EOH
  ./mountdbroots.sh 
  EOH
end

bash "enablecorefiles" do
  user "root"
  cwd "/root"
  code <<-EOH
  sed -i 's/#\*.*soft.*core.*0/\* soft core unlimited/g' /etc/security/limits.conf
  EOH
end

case node[:platform_family]
  when "debian"
    case node[:platform]
      when "debian"
        bash "nfs-domain" do
          user "root"
          cwd "/root"
          code <<-EOH
          sed -i 's/Domain = localdomain/Domain = calpont.com/' /etc/idmapd.conf ; service nfs-common restart
          EOH
        end
      when "ubuntu"
        bash "nfs-domain" do
          user "root"
          cwd "/root"
          code <<-EOH
          sed -i 's/# Domain = localdomain/Domain = calpont.com/' /etc/idmapd.conf
          EOH
        end
    end

  when "rhel"
    bash "nfs-domain" do
      user "root"
      cwd "/root"
      code <<-EOH
      sed -i 's/#Domain = local.domain.edu/Domain = calpont.com/' /etc/idmapd.conf ; service nfs restart
      EOH
    end
end

