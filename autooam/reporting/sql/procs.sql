#
# Creates stored procedures used for autooam reporting.
#

DELIMITER // 

#
# Lists the configs for a particular run.
#
drop procedure if exists get_runConfigs;
create procedure get_runConfigs(
    in inRunId int
)
begin
	select runId,
        runConfigId,
        rc.name name,
        clusterId,
        idbVersion,
        emVersion,
        boxType,
        configName,
        start,
        if(rc.stop is null, timediff(now(), start), timediff(rc.stop, start)) runTime,
        rc.status status,
        passed,
        failed,
        startupPassed,
        startupFailed,
        idbUser,
        datDup,
        binaryInstallation,
        storage,
        pm_query,
        group_concat(distinct rct.comments) testComments,
        group_concat( case when rct.status = "Failed" then rct.description else NULL end ) testFails
	from runConfig rc
    join runConfigTest rct using (runId, runConfigId)
    where runId = inRunId
    group by runId, runConfigId
	order by runConfigId desc;
end // 

#
# Lists the run attributes for a particular run.
#
drop procedure if exists get_run;
create procedure get_run(
    in inRunId int
)
begin
	select 
        r.runId runId,
        r.autoOamVersion version,
        r.status status,
        r.start start,
        if(r.stop is null, timediff(now(), r.start), timediff(r.stop, r.start)) runTime,
        r.passed,
        r.failed,
        r.host,
        group_concat(distinct rc.idbVersion) idbVersions,
        r.description description
	from run r
    join runConfig rc using (runId)
    where runId = inRunId
    group by 1;
end // 

#
# Lists the test details for a particular run / config.
#
drop procedure if exists list_runConfig_details;
create procedure list_runConfig_details(
    in inRunId int,
    in inRunConfigId int
)
begin
	select runId,
        runConfigId,
        name,
        description,
        status,
        runTime,
        comments
	from runConfigTest
    where runId = inRunId and
          runConfigId = inRunConfigId;
end // 

#
# Lists the test details for a particular run / config.
#
drop procedure if exists get_runConfigTest;
create procedure get_runConfigTest(
    in inRunId int,
    in inRunConfigId int,
    in inName varchar(20)
)
begin
	select runId,
        runConfigId,
        name,
        description,
        status,
        runTime,
        comments
	from runConfigTest
    where runId = inRunId and
          runConfigId = inRunConfigId and
          name = inName;
end // 

#
# Start a run.
#
drop procedure if exists start_run;
create procedure start_run(
    in aAutoOamVersion varchar(20),
    in aHost varchar(20),
    out inRunId int) 
begin
    insert into run 
        (autoOAMVersion, host, start, status) 
    values 
        (aAutoOamVersion, aHost, now(), 'In Progress');

    select last_insert_id() into inRunId;
end //

#
# Stop a run.
#
drop procedure if exists stop_run;
create procedure stop_run(
    in inRunId int,
    in successCode int) /* TODO:  Get rid of this - figure out why Python doesn't like calls with single parm */
begin

    /* Get the max runConfigId for this run */
    declare lRunConfigId int default 0;
    select ifnull(max(runConfigId), 0) 
    into lRunConfigId
    from runConfig 
    where runId = inRunId;

    /* Close out the last cluster for this run if there is one */    
    if lRunConfigId > 0 then
        call stop_config(inRunId, lRunConfigId);
    end if;

    /* Close out the run */
    update run  
    set stop=now(),  
        status=if(failed > 0, 'Failed', if(passed > 0, 'Passed', 'Not Run')) 
    where runId = inRunId;

    select 1 into successCode;
end //

#
# Stop a configuration.
#
drop procedure if exists stop_config;
create procedure stop_config(
    in inRunId int,
    in inRunConfigId int)
begin
    update runConfig  
    set stop=now(),  
        status=if(failed > 0, 'Failed', if(passed > 0, 'Passed', 'Not Run')) 
    where runId = inRunId and runConfigId = inRunConfigId;

end //

#
# Create a configuration.
#
drop procedure if exists start_config;
create procedure start_config(
    in inRunId int,
    in inName varchar(30),
    in inClusterId varchar(50),
    in inIdbVersion varchar(20),
    in inBoxType varchar(20), 
    in inConfigName varchar(20),
    in inIdbUser varchar(10),
    in inDatDup varchar(10),
    in inBinaryInstallation varchar(10),
    in inStorage varchar(10)
)
begin
    /* Get next runConfigId - values are 1..n for a run */
    declare lRunConfigId int default 0;
    select ifnull(max(runConfigId), 0) + 1 
    into lRunConfigId
    from runConfig 
    where runId = inRunId;

    /* Close out the prior cluster for this run if there is one */    
    if lRunConfigId > 1 then
        call stop_config(inRunId, lRunConfigId -1);
    end if;

    insert into runConfig 
        (runId, runConfigId, name, clusterId, idbVersion, boxType, configName, 
         start, status, idbUser, datDup, binaryInstallation, storage) 
    values 
        (inRunId, lRunConfigId, inName, inClusterId, inIdbVersion, inBoxType, inConfigName, 
         now(), 'In Progress', inidbUser, inDatDup, inBinaryInstallation, inStorage);
end //

#
# Create a configuration - v2 with pm_query option
#
drop procedure if exists start_config;
create procedure start_config(
    in inRunId int,
    in inName varchar(30),
    in inClusterId varchar(50),
    in inIdbVersion varchar(20),
    in inBoxType varchar(20), 
    in inConfigName varchar(20),
    in inIdbUser varchar(10),
    in inDatDup varchar(10),
    in inBinaryInstallation varchar(10),
    in inStorage varchar(10),
    in inPmQuery varchar(10)
)
begin
    /* Get next runConfigId - values are 1..n for a run */
    declare lRunConfigId int default 0;
    select ifnull(max(runConfigId), 0) + 1 
    into lRunConfigId
    from runConfig 
    where runId = inRunId;

    /* Close out the prior cluster for this run if there is one */    
    if lRunConfigId > 1 then
        call stop_config(inRunId, lRunConfigId -1);
    end if;

    insert into runConfig 
        (runId, runConfigId, name, clusterId, idbVersion, boxType, configName, 
         start, status, idbUser, datDup, binaryInstallation, storage, pm_query) 
    values 
        (inRunId, lRunConfigId, inName, inClusterId, inIdbVersion, inBoxType, inConfigName, 
         now(), 'In Progress', inidbUser, inDatDup, inBinaryInstallation, inStorage, inPmQuery);
end //

#
# Create a configuration - v3 with pm_query and emVersion
#
drop procedure if exists start_config;
create procedure start_config(
    in inRunId int,
    in inName varchar(30),
    in inClusterId varchar(50),
    in inIdbVersion varchar(20),
    in inBoxType varchar(20), 
    in inConfigName varchar(20),
    in inIdbUser varchar(10),
    in inDatDup varchar(10),
    in inBinaryInstallation varchar(10),
    in inStorage varchar(10),
    in inPmQuery varchar(10),
    in inEmVersion varchar(20)
)
begin
    /* Get next runConfigId - values are 1..n for a run */
    declare lRunConfigId int default 0;
    select ifnull(max(runConfigId), 0) + 1 
    into lRunConfigId
    from runConfig 
    where runId = inRunId;

    /* Close out the prior cluster for this run if there is one */    
    if lRunConfigId > 1 then
        call stop_config(inRunId, lRunConfigId -1);
    end if;

    insert into runConfig 
        (runId, runConfigId, name, clusterId, idbVersion, boxType, configName, 
         start, status, idbUser, datDup, binaryInstallation, storage, pm_query, emVersion) 
    values 
        (inRunId, lRunConfigId, inName, inClusterId, inIdbVersion, inBoxType, inConfigName, 
         now(), 'In Progress', inidbUser, inDatDup, inBinaryInstallation, inStorage, inPmQuery, inEmVersion);
end //

#
# Add test result.
#
drop procedure if exists add_runConfigTest;
create procedure add_runConfigTest(
    in inRunId int,
    in inRunConfigId int,
    in inTestName varchar(20),
    in inTestDesc varchar(100),
    in inStatus varchar(20),
    in inRunTime varchar(20)
)
begin

    /* Add the test run. */
    insert into runConfigTest (
        runId,
        runConfigId,
        name,
        description,
        status,
        runTime,
        stop
    )
    values (
        inRunId,
        inRunConfigId,
        inTestName,
        inTestDesc,
        inStatus,
        inRunTime,
        now()
    );

    /* Update the passed / failed count in runConfig and run. */
    if inTestName = 'startup' then
        if inStatus = 'Passed' then
            update run set startupPassed = startupPassed + 1 where runId = inRunId;
            update runConfig set startupPassed = startupPassed + 1 where runId = inRunId and runConfigId = inRunConfigId;
        else
            update run set startupFailed = startupFailed + 1 where runId = inRunId;
            update runConfig set startupFailed = startupFailed + 1 where runId = inRunId and runConfigId = inRunConfigId;
        end if;
    else
        if inStatus = 'Passed' then
            update run set passed = passed + 1 where runId = inRunId;
            update runConfig set passed = passed + 1 where runId = inRunId and runConfigId = inRunConfigId;
        else
            update run set failed = failed + 1 where runId = inRunId;
            update runConfig set failed = failed + 1 where runId = inRunId and runConfigId = inRunConfigId;
        end if;
    end if;

end //

#
# Edit runConfigTest.comments.
#
drop procedure if exists edit_runConfigTest;
create procedure edit_runConfigTest (
    in inRunId int,
    in inRunConfigId int,
    in inName varchar(20),
    in inComments varchar(1000)
)
begin
    update runConfigTest 
    set comments=if(length(trim(inComments))=0, null, inComments) 
    where runId = inRunId and runConfigId = inRunConfigId and name = inName;
end //
    
DELIMITER ;

