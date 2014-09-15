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

bash "upgrade_binary_idb" do
  user "#{node[:idbuser]}"
  cwd "#{homedir}"
  code <<-EOH
  # expect this to run from /home/<idbuser> as <idbuser>
  if [ "#{node[:idbuser]}" = "root" ]; 
  then
    #{idbinstalldir}/bin/pre-uninstall
  else
    #{idbinstalldir}/bin/pre-uninstall --installdir=#{idbinstalldir}
  fi

  mv #{idbinstalldir}/etc/Calpont.xml #{idbinstalldir}/etc/Calpont.xml.rpmsave
  
  tar -zxf "/packages/#{node[:upgfile]}" -C #{tardir} 
  
  # copy over the package file for remote installs
  cp /packages/#{node[:upgfile]} /#{homedir}/.
  
  if [ "#{node[:idbuser]}" = "root" ]; 
  then
    #{idbinstalldir}/bin/post-install
  else
    #{idbinstalldir}/bin/post-install --installdir=#{idbinstalldir}
  fi
  EOH
end

bash "fixup_calpontxml" do
  user "#{node[:idbuser]}"
  cwd "#{homedir}"
  code <<-EOH
  sed -i 's/<DBRootStorageType>local<\\/DBRootStorageType>/<DBRootStorageType>internal<\\/DBRootStorageType>/' #{idbinstalldir}/etc/Calpont.xml.rpmsave
  EOH
end

bash "upgrade_binary_postconfigure" do
  user "root"
  cwd "#{homedir}"
  code <<-EOH
  su - #{node[:idbuser]} -c "#{idbinstalldir}/bin/postConfigure -p '#{password}' -n -c #{idbinstalldir}/etc/Calpont.xml.rpmsave"
  EOH
end

