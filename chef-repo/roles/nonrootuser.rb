# setup passwordless sudo for the infinidb user

name "nonrootuser"
description "this is a role for setting up a non-root user install"
run_list "recipe[autooam::base]","recipe[autooam::nonrootuser]","recipe[sudo::default]"

default_attributes(
  "authorization" => {
    "sudo" => {
      "groups" => ["admin", "wheel", "sysadmin"],
      "users" => ["calpont", "vagrant"],
      "passwordless" => true,
      "sudoers_defaults" => [ 'env_reset', 'secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"' ]
    }
  }
)

