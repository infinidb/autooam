name "root_key"
description "this is a role for root user cluster install via ssh keys"
run_list "recipe[autooam::base]", "recipe[autooam::rootsshkey]"
