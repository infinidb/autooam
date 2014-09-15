#!/bin/bash

echo "utils/infinidb_not_running.sh:"

# glusterfs does not shut down with Infinidb
ps -ef |grep Cal|grep -v grep|grep -v glusterfs
ret=$?
# we need to invert the results - if grep finds something then
# infinidb is still running and we need to return 1/false
if [ $ret -ne 0 ]; then
  exit 0
else
  exit 1
fi
