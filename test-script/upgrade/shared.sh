#!/bin/bash

if [ -z "$INFINIDB_INSTALL_DIR" ]; then
        INFINIDB_INSTALL_DIR="/usr/local/Calpont"
        export INFINIDB_INSTALL_DIR
fi

if [ -z "$MYSQLCMD" ]; then
        MYSQLCMD="$INFINIDB_INSTALL_DIR/mysql/bin/mysql --defaults-file=$INFINIDB_INSTALL_DIR/mysql/my.cnf -u root"
        export MYSQLCMD
fi

DB=dbFunctional
ROWSPERLOAD=100000

#
# Runs a sql statement and exits returning 1 if there is an error.
#
runSql() {
	sql=$1
	$MYSQLCMD -n -vvv -e "$sql"
	if [ $? -ne 0 ]; then
		exit 1
	fi
}

#
# Returns the date and time with nanoseconds included.
#
getDate() {
    date '+%Y-%m-%d %H:%M:%S.%N'
}

#
# Validate data.
# 
validate() {	

	# Make sure there is at least one load.
	sql="select count(*) from loads;"
	count=`$MYSQLCMD $DB --skip-column-names -e "$sql"`
	if [ $count -lt 0 ]; then
		echo "Load count is 0.  Should be >= 1."
		exit 1
	fi

	# Run a few selects to validate that the loads table jives with the t1 table and 
	# that the batch sizes are correct.
	table=batch$count
	sql="
		select max(batch) into @batches from loads;
		select if(count(distinct batch)=@batches, 'good', 'bad') status from t1;
		select batch, 
		       count(c1), 
		       if(count(c1) = $ROWSPERLOAD, 'good', 'bad') c1_status, 
		       if(count(c2) = $ROWSPERLOAD, 'good', 'bad') c2_status
		from t1
		group by 1
		order by 1;
		select if(c1=@batches, 'good', 'bad') status, if(c2=@batches, 'good', 'bad') status2 from $table;
	"
	$MYSQLCMD $DB --table -n -e "$sql" > validation.log 2>&1
	echo ""
	echo "Validation Results:"
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
}

#
# Echo a message for each processing step.
#
outputStep() {
	msg=$1
	echo ""
	echo "$msg at `getDate`."
}

