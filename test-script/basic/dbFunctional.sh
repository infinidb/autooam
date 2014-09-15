#!/bin/bash

# 1) Creates a one column table.
# 2) Imports 160,000 rows.
# 3) Deletes every 10,000th row
# 4) Validates with a count of the table.

getDate() {
    date '+%Y-%m-%d %H:%M:%S.%N'
}

DB=dbFunctional
TABLE=dbFunctional
ROWS=160000
DELETEEVERYNTH=10000
let ROWSAFTERDELETE=$ROWS-$ROWS/$DELETEEVERYNTH;

if [ -z "$INFINIDB_INSTALL_DIR" ]; then
        INFINIDB_INSTALL_DIR="/usr/local/Calpont"
        export INFINIDB_INSTALL_DIR
fi

if [ -z "$MYSQLCMD" ]; then
        MYSQLCMD="$INFINIDB_INSTALL_DIR/mysql/bin/mysql --defaults-file=$INFINIDB_INSTALL_DIR/mysql/my.cnf -u root"
        export MYSQLCMD
fi

echo ""
echo "1) Dropping table if exists and creating table at `getDate`."
sql="create database if not exists $DB; use $DB; drop table if exists $TABLE; create table $TABLE(c1 int)engine=infinidb;"
$MYSQLCMD -vvv -n -e "$sql"
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "Create table failed at `getDate`."
	exit $rtn
fi

echo ""
echo "2) Importing rows at `getDate`."
echo "" | awk -v rows=$ROWS '{for(i=1; i<=rows; i++)print i}' | $INFINIDB_INSTALL_DIR/bin/cpimport $DB $TABLE
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "Import failed at `getDate`."
	exit $rtn
fi

echo ""
echo "3) Deleting rows at `getDate`."
sql="delete from $TABLE where c1%$DELETEEVERYNTH = 0;"
$MYSQLCMD $DB -vvv -n -e "$sql"
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "Delete failed at `getDate`."
	exit $rtn
fi

echo ""
echo "4) Validating at `getDate`."
sql="select count(*) from $TABLE;"
count=`$MYSQLCMD $DB --skip-column-names -e "$sql"`
rtn=$?
if [ $rtn -ne 0 ]; then
	echo "Select failed at `getDate`."
	exit $rtn
fi

if [ $count -ne $ROWSAFTERDELETE ]; then
	echo "Count incorrect.  Count is $count.  Expected $ROWSAFTERDELETE at `getDate`."
	exit 1
fi

#needed for combo 2pm failover testing
echo ""
echo "5) Dropping table"
sql="use $DB; drop table if exists $TABLE;"
$MYSQLCMD -vvv -n -e "$sql"
rtn=$?
if [ $rtn -ne 0 ]; then
        echo "Drop table failed at `getDate`."
        exit $rtn
fi

echo ""
echo "Success at `getDate`."
exit 0
