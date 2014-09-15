# we have to set a root password because we need to pass
# a password to postConfigure so that it can run in no-prompt
# and it won't accept an empty passwoard
case node[:platform_family]
  when "debian"
    ssh_service = 'ssh'
    # a bit uglier on debian family as we don't have the passwd
    # option to set from command-line
    bash "root_password_set" do
      user "root"
      cwd "/root"
      flags '-x'
      code <<-EOH
      sed -i 's/^root.*$/root:\\$6\\$RCn1gIG\\/qUVNc\\$\\/I22d.a\\/Q65BGv\\/gd3izzYFcFg6thNSXMPx5JQ\\.nlPcM\\.TGEI\\/wZIIfIFjLukbm\\.6G9djzvkrl5aB\\/TYvZraO\\.:15597:0:99999:7:::/' /etc/shadow 
      EOH
    end
  when "rhel"
    ssh_service = 'sshd'
    bash "root_password_set" do
      user "root"
      cwd "/root"
      code <<-EOH
      echo "qalpont!" | passwd --stdin root
      EOH
    end
end

directory "/root/.ssh" do
  owner "root"
  group "root"
  mode 00700
  action :create
end

cookbook_file "/root/.ssh/authorized_keys" do
  source "authorized_keys"
  mode 0600
  owner "root"
  group "root"
end

cookbook_file "/root/.ssh/id_rsa" do
  source "insecure_private_key"
  mode 0600
  owner "root"
  group "root"
end

bash "StrictHostKey_disable" do
  user "root"
  cwd "/root"
  flags '-x'
  code <<-EOH
  sed -i 's/^.*StrictHostKeyChecking.*$/StrictHostKeyChecking=no/' /etc/ssh/ssh_config ; service #{ssh_service} restart
  EOH
end


