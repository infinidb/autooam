group "#{node[:idbuser]}" do
  gid 1100
  action :create
end

homedir = "/home/#{node[:idbuser]}"

user "#{node[:idbuser]}" do
  comment "InfiniDB User"
  uid 1100
  gid "#{node[:idbuser]}"
  home "#{homedir}"
  shell "/bin/bash"
  # password is infinidb
  # trying to avoid this with chef because it requires some ruby-gem we don't have
  #  password "$6$TQAeoUYBe$pvJ6TUfdR3yYOWPDowd5IsREhwktHmRR8FSIw.s08ZL3zqu6NzCNrDaGKiAD7xFfNMV1X9ELdcf50t7ERyQvs/"
  supports :manage_home=>true
  action :create
end

bash "nonroot_password_set" do
  user "root"
  cwd "/root"
  flags '-x'
  code <<-EOH
  sed -i 's/^#{node[:idbuser]}.*$/#{node[:idbuser]}:\\$6\\$TQAeoUYBe$pvJ6TUfdR3yYOWPDowd5IsREhwktHmRR8FSIw\\.s08ZL3zqu6NzCNrDaGKiAD7xFfNMV1X9ELdcf50t7ERyQvs\\/:15597:0:99999:7:::/' /etc/shadow 
  EOH
end

template "#{homedir}/.bashrc" do
  source "bashrc.erb"
  mode 0644
  owner "#{node[:idbuser]}"
  group "#{node[:idbuser]}"
  variables({
    :idbuser => node[:idbuser]
  })
end

directory "#{homedir}/.ssh" do
  owner "#{node[:idbuser]}"
  group "#{node[:idbuser]}"
  mode 00700
  action :create
end

cookbook_file "#{homedir}/.ssh/authorized_keys" do
  source "altuser_authorized_keys"
  mode 0600
  owner "#{node[:idbuser]}"
  group "#{node[:idbuser]}"
end

cookbook_file "#{homedir}/.ssh/id_rsa" do
  source "altuser_private_key"
  mode 0600
  owner "#{node[:idbuser]}"
  group "#{node[:idbuser]}"
end

case node[:platform_family]
  when "debian"
    ssh_service = 'ssh'
  when "rhel"
    ssh_service = 'sshd'
end

bash "StrictHostKey_disable" do
  user "root"
  cwd "/root"
  code <<-EOH
  sed -i 's/^.*StrictHostKeyChecking.*$/StrictHostKeyChecking=no/' /etc/ssh/ssh_config ; service #{ssh_service} restart
  EOH
end

