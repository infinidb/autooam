case node[:platform_family]
  when "debian"

  bash "machines_setup" do
    user "root"
    cwd "/root"
    code <<-EOH
    grep -v '^#' /etc/hosts | perl -ne 'print "$1$2 pdsh_rcmd_type=ssh\\n" if /(pm|um)([0-9+])(\n)/' > /etc/genders
    EOH
  end

  when "rhel"

  bash "machines_setup" do
    user "root"
    cwd "/root"
    code <<-EOH
    grep -v '^#' /etc/hosts | perl -ne 'print "$1$2\\n" if /(pm|um)([0-9+])(\n)/' > /etc/pdsh/machines
    EOH
  end

end


