#!/bin/bash

# 1) Creates tpchc database
# 2) Creates TPCH tables
# 3) Cpimport 1g lineitem
# 4) execute aggregation queries
# 5) LDI 1g lineitem
# 6) execute aggregation queries
# 7) update l_quantity = -1

dbName=tpchc
testPath=/mnt/autooam/test-script/upgrade
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
echo "1) newInstall - Creating TPCH database."
sql="create database if not exists $dbName;"
$MYSQLCMD -vvv -n -e "$sql"
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "newInstall - Create TPCH database failed."
	exit $rtn
fi

echo ""
echo "2) newInstall - Creating TPCH table."
$MYSQLCMD $dbName -vvv -n < $testPath/createTPCH100GBIDB.sql
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "newInstall - Create TPCH tables failed."
	exit $rtn
fi

echo ""
echo "3) newInstall - Importing rows."
$INFINIDB_INSTALL_DIR/bin/cpimport $dbName lineitem $refPath/lineitem.tbl
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "newInstall - cpimport lineitem failed."
	exit $rtn
fi

echo ""
echo "4) newInstall - get import result"
sql="select min(l_orderkey), max(l_orderkey), avg(l_orderkey), min(l_extendedprice), max(l_extendedprice), avg(l_extendedprice) from lineitem;"
$MYSQLCMD $dbName -n -e "$sql" > queryResult_newInstall.txt
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "newInstall - get import result failed."
	exit $rtn
fi

# killed steps 5 & 6 - was LDI of same data set and repeat of above select

echo ""
echo "7) newInstall - update l_quantity."
sql="update lineitem set l_quantity = -1;"
$MYSQLCMD $dbName -vvv -n -e "$sql"
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "newInstall - Update failed."
	exit $rtn
fi

echo "Success."
exit 0
