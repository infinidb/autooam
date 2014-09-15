#!/bin/bash

# This script is used for autooam upgrade validation.  
#
# For a new installation, pass new as the parameter.  The script does the following:
# 1) Creates the dbFunctional.loads and dbFunctional.t1 tables if they don't already exist.
# 2) Inserts a load row to track a new batch of rows.
#    Imports a batch of 100,000 rows.
#    Updates the load row.
# 3) Runs validation queries.
# 
# For an upgrade, pass upgrade as the parameter.  The script does the following:
# 1) Runs validation queries for prior batches of rows.
# 2) Inserts a load row to track a new batch of rows.
#    Imports a batch of 100,000 rows.
#    Updates the load row.
# 3) Runs validation queries.
#
# NOTE:  
# The upgrade option is dependent on the script having been run at least one time prior with the "new" parameter.
# 
# The script returns 0 if everything is successful, otherwise 1.

script_dir=$(dirname $0)
source $script_dir/shared.sh

#
# Create tables.
#
createTables() {
	runSql "create database if not exists $DB;"
	runSql "create table if not exists $DB.loads(batch int, started datetime, finished datetime)engine=infinidb;"
	runSql "create table if not exists $DB.t1(batch int, c1 int, c2 varchar(10))engine=infinidb;"
}

#
# Show usage and exit.
#
usage() {
	echo ""
	echo "This script takes a single parameter - new or upgrade."
	echo "If no parameter is provided, default is new."
	echo ""
	exit 1
}

#
# Loads a new batch of rows.
#
loadBatch() {

	# Get the highest existing batch number.
	batch=`$MYSQLCMD $DB --skip-column-names -n -e "select ifnull(max(batch), 0) from loads;"`
	if [ $? -ne 0 ]; then
		echo "Error selecting max(batch) in loadBatch."
		exit 1
	fi
	
	# Load the new batch.
	let batch++;
	runSql "insert into $DB.loads values ($batch, now(), null);"
	echo "" | awk -v batch=$batch -v rows=$ROWSPERLOAD '{for(i=1; i<=rows; i++)print batch "|" i "|" i}' | $INFINIDB_INSTALL_DIR/bin/cpimport $DB t1
	if [ $? -ne 0 ]; then
        	echo "Import failed at `getDate`."
	        exit 1
	fi
	runSql "update $DB.loads set finished=now();"

	# Create a new table to go with the batch.  This will be used by replication validation.
	tbl=batch$batch
	runSql "create table $DB.$tbl(c1 int)engine=infinidb; alter table $DB.$tbl add column c2 int; insert into $DB.$tbl values($batch, $batch);"
}

##############################################################################################
# Main processing.
##############################################################################################

#
# Validate parameter  - "new" or "upgrade".
#
if [ $# -lt 1 ]; then
	installationType="new"
else
	installationType=$1
fi

echo $installationType

if [ "$installationType" == "new" ]; then
	outputStep "New Installation."
	outputStep "1) Create tables"
	createTables
elif [ "$installationType" == "upgrade" ]; then
	outputStep "Upgrade."
	outputStep "1) Validate pre existing data"
	validate
else
	usage
fi

outputStep "2) Load a new batch of rows"
loadBatch

outputStep "3) Validate the new batch of rows"
validate

echo ""
outputStep "Success"
exit 0
