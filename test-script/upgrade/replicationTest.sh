#!/bin/bash
script_dir=$(dirname $0)
source $script_dir/shared.sh

usage() {
	echo
	echo "A single parameter is required - replication or pmWithUm."
	echo 
	exit 1
}

#
# Step 1.  Validate parameter.
#
outputStep "1) Validate parameter passed to script"
if [ $# -ne 1 ]; then
	usage
fi
type=$1
if [ "$type" != "replication" ] && [ "$type" != "pmWithUm" ]; then
	usage
fi 

#
# Step 2.  Validate configurables.
#
outputStep "2) Validate that configurables are correct based on parameter"
serverTypeInstall=`$INFINIDB_INSTALL_DIR/bin/getConfig Installation ServerTypeInstall` # 1 (separate) or 2 (combo)
if [ $serverTypeInstall -lt 1 ] || [ $serverTypeInstall -gt 2 ]; then
	echo "Installation/ServerTypeInstall is $serverTypeInstall.  Must be 1 or 2."
	exit 1
fi
mysqlRep=`$INFINIDB_INSTALL_DIR/bin/getConfig Installation MySQLRep`
if [ "$mysqlRep" != "y" ]; then
	echo "Installation/MySQLRep is set to '$mysqlRep'.  It must be set to 'y'."
	exit 1
fi
pmWithUm=`$INFINIDB_INSTALL_DIR/bin/getConfig Installation PMwithUM`
if [ "$type" == "pmWithUm" ]; then
	if [ "$pmWithUm" != "y" ]; then
		echo "Installation/PMwithUM is set to '$pmWithUm' and should by 'y' as the script was called with the pmWithUm parameter set."
		exit 1
	fi
else
	if [ "$pmWithUm" == "y" ]; then
		echo "Installation/PMwithUM is set to 'y' and should not be as the pmWithUm parameter was not passed."
		exit 1
	fi
fi
module=`cat $INFINIDB_INSTALL_DIR/local/module`
moduleType=`echo $module | awk '{print substr($1, 1, 2)}'`
if [ "$moduleType" != "pm" ] && [ "$moduleType" != "um" ]; then
	echo "Invalid module $module.  Expected a pm or um such as pm1, um1, etc."
	exit 1	
fi
if [ "$pmWithUm" == "y" ] && [ $serverTypeInstall -eq 2 ]; then
	echo "ServerTypeInstall is 2 (combo) and PMwithUM is 'y'.  Invalid combination."
	exit 1
fi

#
# Step 3.  Validate that a pure UM sees all data.
#
outputStep "3) Validate that pure UM can see the full database"
if [ "$moduleType" == "um" ]; then
	validate
else
	echo "Module type is '$moduleType'.  No validation performed."
fi

#
# Step 4.  Validate that a pure UM receives error issuing a select with local query set .
#
outputStep "4) Validate that pure UM gets IDB-2047 error running a query with infinidb_local_query=1"
if [ "$moduleType" == "um" ]; then
	sql="set infinidb_local_query=1; select * from t1;" 
	$MYSQLCMD $DB -vvv -e "$sql" > validate.log 2>&1
	cat validate.log
	match=`grep "IDB-2047" validate.log | wc -l`
	if [ $match -lt 1 ]; then
		echo "IDB-2047 was not returned.  Validation failed."
		exit 1
	fi
else
	echo "Module type is '$moduleType'.  No validation performed."
fi
	
#
# Step 5.  Validate that PM sees all data on a combo system.
#
outputStep "5) Validate that PM can see the full database if this is a combo system"
if [ $serverTypeInstall -eq 2 ]; then
	if [ "$moduleType" == "pm" ]; then
		validate
	else
		echo "Module type is '$moduleType'.  No validation performed."
	fi
else
	echo "ServerTypeInstall is '$serverTypeInstall' which is not a combo system.  No validation performed."
fi

#
# Step 6.  Validate that a pure UM sees local data by default when PMwithUM is set.
#
outputStep "6) Validate that PM has infinidb_local_query=1 and only sees local data if PMwithUM is set to 'y'"
if [ "$pmWithUm" == "y" ] && [ "$moduleType" == "pm" ]; then
	moduleNum=`echo $module | awk '{print substr($1, 3, 99)}'`
	sql="
		select if(@@infinidb_local_query=1, 'good', 'bad') result;
		select idbpm(c1), if(idbpm(c1)=$moduleNum, 'good', 'bad') result, count(*) from t1 group by 1, 2;
	"
	$MYSQLCMD $DB --table -n -e "$sql" > validation.log 2>&1
	cat validation.log
	errors=`grep -i error validation.log | wc -l`
	badResults=`grep bad validation.log | grep -v select | wc -l`
	rm validation.log
	if [ $errors -gt 0 ]; then
		echo "Errors during validation."
		exit 1
	elif [ $badResults -gt 0 ]; then
		echo "Incorrect result during validation."
		exit 1
	fi
else
	echo "PMwithUM is '$pmWithUm' and module is '$module'.  No validation performed."
fi

#
# Step 7.  Validate that a pure PM sees all data when local_query turned off..
#
outputStep "7) Validate that pure PM sees all data with local query off"
if [ "$moduleType" == "pm" ] && [ "$pmWithUm" == "y" ]; then
	$MYSQLCMD -e "set global infinidb_local_query=0;"
	validate
	$MYSQLCMD -e "set global infinidb_local_query=1;"
else
	echo "Module type is '$moduleType' and PMwithUM is '$pmWithUm'.  No validation performed."
fi

exit 0
