#!/bin/bash

# 1) Cpimport 1g lineitem
# 2) execute aggregation queries
# 3) LDI 1g lineitem
# 4) execute aggregation queries
# 5) update l_quantity = -1
# 6) Validate

dbName=tpchc
refPath=/mnt/opt-autooam

if [ -z "$INFINIDB_INSTALL_DIR" ]; then
        INFINIDB_INSTALL_DIR="/usr/local/Calpont"
        export INFINIDB_INSTALL_DIR
fi

if [ -z "$MYSQLCMD" ]; then
        MYSQLCMD="$INFINIDB_INSTALL_DIR/mysql/bin/mysql --defaults-file=$INFINIDB_INSTALL_DIR/mysql/my.cnf -u root"
        export MYSQLCMD
fi

echo ""
echo "1) upgrade - Importing rows."
$INFINIDB_INSTALL_DIR/bin/cpimport $dbName lineitem $refPath/lineitem.tbl
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "upgrade - cpimport lineitem failed."
	exit $rtn
fi

echo ""
echo "2) upgrade - get import result"
sql="select min(l_orderkey), max(l_orderkey), avg(l_orderkey), min(l_extendedprice), max(l_extendedprice), avg(l_extendedprice) from lineitem;"
$MYSQLCMD $dbName -n -e "$sql" > queryResult_upgrade.txt
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "upgrade - get import result failed."
	exit $rtn
fi

# killed steps 3 & 4 - was LDI of same data set and repeat of above select

echo ""
echo "5) upgrade - update l_quantity."
sql="update lineitem set l_quantity = -1;"
$MYSQLCMD $dbName -vvv -n -e "$sql"
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "upgrade - Update failed."
	exit $rtn
fi

echo ""
echo "6) Validating."
diff queryResult_newInstall.txt queryResult_upgrade.txt >queryResult_diff.txt
count=`cat queryResult_diff.txt |wc -l`
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "upgrade - post-upgrade validation failed."
	exit $rtn
fi

echo "Success."
exit 0
