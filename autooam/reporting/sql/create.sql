create database if not exists autooam;

create table run (
    runId int not null auto_increment,
    autoOAMVersion varchar(20),
    host varchar(100),
    status varchar(20) not null,
    start datetime not null,
    stop datetime,
    passed int default 0,
    failed int default 0,
    startupPasssd int default 0,
    startupFailed int default 0,
    description varchar(1000),
    primary key (runId)
);

create table runConfig (
    runId int not null,
    runConfigId int not null,
    name varchar(30) not null,
    clusterId varchar(50) not null,
    idbVersion varchar(20) not null,
    boxType varchar(20) not null,
    configName varchar(20) not null,
    idbUser varchar(10) not null,
    datDup varchar(10) not null,
    binaryInstallation varchar(10) not null,
    storage varchar(10) not null,
    pm_query varchar(10),
    emVersion varchar(20),
    start datetime not null,
    stop datetime,
    status varchar(20) not null,
    passed int default 0,
    failed int default 0,
    startupPasssd int default 0,
    startupFailed int default 0,
    primary key (runId, runConfigId)
);

create table runConfigTest (
    runId int not null,
    runConfigId int not null,
    name varchar(20) not null,
    description varchar(100) not null,
    status varchar(20) not null,
    runTime varchar(20) not null,
    stop datetime not null,
    comments varchar(1000)
);
