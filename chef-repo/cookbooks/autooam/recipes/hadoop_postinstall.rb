case node[:platform_family]
  when "debian"

    bash "install_libhdfs" do
      user "root"
      cwd "/root"
      code <<-EOH
      apt-get -y install libhdfs0
      EOH
    end

  when "rhel"

    bash "install_libhdfs" do
      user "root"
      cwd "/root"
      code <<-EOH
      yum -y install hadoop-libhdfs
      EOH
    end

end

