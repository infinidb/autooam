<html>
<head>
<meta http-equiv="refresh" content="60" >
</head>
<body>
<a href='<?php $_SERVER['PATH_INFO'] ?>'>AutoOAM Nightly Results</a>
<br>
<br>
<form action="<?php $_SERVER['PATH_INFO'] ?>" method="get">
<table>
    <tr>
        <td>Days To Show:</td>
        <td>
        <select name="days" id="days">
            <option value="All" <?php if ($_GET["days"]=="All") echo "selected"; ?>>All</option>
            <option value="0.5" <?php if ($_GET["days"]=="0.5") echo "selected"; ?>>0.5</option>
            <option value="1"  <?php if ($_GET["days"]=="1") echo "selected"; ?>>1</option>
            <option value="7" <?php if ($_GET["days"]=="7") echo "selected"; ?>>7</option>
            <option value="30" <?php if ($_GET["days"]=="30" or !$_GET["days"]) echo "selected"; ?>>30</option>
        </select>
        </td>
    </tr>
    <tr>
        <td>Host Contains:</td>
        <td><input type='text' id='host' name='host' value='<?php echo $_GET["host"]; ?>'></td>
    </tr>
    <tr>
        <td>Start Contains:</td>
        <td><input type='text' id='start' name='start' value='<?php echo $_GET["start"]; ?>'></td>
    </tr>
    <tr>
        <td>Version Contains:</td>
        <td><input type='text' id='version' name='version' value='<?php echo $_GET["version"]; ?>'></td>
    </tr>
</table>
<input type="hidden" name="unit" id="unit" value="<?php echo $_GET["unit"]; ?>"/>
<input type="submit">
<br>
<br>
<?php
header('Cache-Control: no-cache, no-store, must-revalidate'); // HTTP 1.1. 
header('Pragma: no-cache'); // HTTP 1.0. 
header('Expires: 0'); // Proxies.
$con = mysql_connect('localhost','root','',false,65536);
if ($_GET["unit"]) {
    $db="autooam_unit";
}
else {
    $db="autooam";
}
mysql_select_db ($db);

$hoursToShow=30*24;
if (isset($_GET["days"])) {
    if ($_GET["days"] == "All") {
        $hoursToShow=10000*24;
    }
    else {
        $hoursToShow=$_GET["days"]*24;
    }
}
$query="select
        r.runId runId,
        r.autoOamVersion version,
        r.status status,
        r.start start,
        if(r.stop is null, timediff(now(), r.start), timediff(r.stop, r.start)) runTime,
        r.passed,
        r.failed,
        r.startupPassed,
        r.startupFailed,
        replace(r.host, '.calpont.com', '') host,
        group_concat(distinct rc.idbVersion) idbVersions,
        group_concat(distinct rc.emVersion) emVersions,
        group_concat(distinct rc.idbVersion) like '%" . $_GET["version"] . "%' versionMatches,
        group_concat(distinct rct.comments order by 1) testComments,
        r.description description
        from run r
    join runConfig rc using (runId)
    join runConfigTest rct on (rc.runId = rct.runId and rc.runConfigId = rct.runConfigId)";

$query .= "where r.start like '%" . $_GET["start"] . "%' and ";
$query .= "      r.host like '%" . $_GET["host"] . "%' and ";
$query .= "      r.start + interval " . $hoursToShow . " hour > now() ";
 

# Using sub select was very expensive and can't use group_concat in the where clause, so instead used the versionMatches column above 
# and compare it in the loop down below.
#$query .= "      r.runId in (select runId from runConfig where idbVersion like '%" . $_GET["version"] . "%') ";

$query .= "
    group by runId
        order by runId desc;
";

$result=mysql_query($query)
or die(mysql_error());

$num=mysql_numrows($result);
mysql_close();
?>
<!-- <table border="1" cellspacing="2" cellpadding="2"> -->
<table border="1" cellspacing="1" cellpadding="2">
<tr>
<th align=left>ID</font></th>
<th align=left>Host</font></th>
<th align=left>Status</font></th>
<th align=left>Start</font></th>
<th align=left>Time</font></th>
<th align=left>Passed</font></th>
<th align=left>Failed</font></th>
<th align=left>Bad Starts</font></th>
<th align=left>Version</font></th>
<th align=left>EM Version</font></th>
<th align=left>Test Comments</font></th>
<th align=left>Description</font></th>
<th align=left>Edit</th>
</tr>

<?php
$i=0;
while ($i < $num) {

$fVersionMatches=mysql_result($result,$i,"versionMatches");
if ($fVersionMatches == 1) {
    $fRunId=mysql_result($result,$i,"runid");
    $fHost=mysql_result($result,$i,"host");
    $fStatus=mysql_result($result,$i,"status");
    $fStart=mysql_result($result,$i,"start");
    $fRuntime=mysql_result($result,$i,"runtime");
    $fPassed=mysql_result($result,$i,"passed");
    $fFailed=mysql_result($result,$i,"failed");
    $fStartupFailed=mysql_result($result,$i,"startupFailed");
    $fIdbVersions=mysql_result($result,$i,"idbVersions");
    $fEmVersions=mysql_result($result,$i,"emVersions");
    $fTestComments=mysql_result($result,$i,"testComments");

    /* Make any numeric testComments link to Bugzilla. */

    $newComments="";
    $comments=explode(",", $fTestComments);
    foreach ($comments as &$x) {
        if (is_numeric($x)) {
            $x="<a href='http://srvengcm1.calpont.com/bugzilla/show_bug.cgi?id=" . $x . "'>" . $x . "</a>"; 
        }
        if ($newComments == "") {
            $newComments=$x;
        }
        else {
            $newComments=$newComments . ", " . $x;
        }
    }
    $fTestComments=$newComments;

    $fDescription=mysql_result($result,$i,"description");
    /* TODO:  Move passed failed red/green logic to a utility function. */
    if ($fStatus == "Passed") {
        $fStatus="<font color=green><b>Passed</b></font>";
    }
    elseif ($fStatus == "Failed") {
        $fStatus="<font color=red><b>Failed</b></font>";
    }
    else {
        if ($fFailed > 0) {
            $fStatus="<font color=red><b>" . $fStatus . "</b></font>";
        }
        elseif ($fPassed > 0) {
            $fStatus="<font color=green><b>" . $fStatus . "</b></font>";
        }
    }

?>

<tr>
<td><a href='autoOamRunDetails.php?runId=<?php echo $fRunId; ?>&db=<?php echo $db; ?>'><?php echo $fRunId; ?></a>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fHost; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fStatus; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fStart; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fRuntime; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fPassed  ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fFailed; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fStartupFailed; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fIdbVersions; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fEmVersions; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td style="width:15%"><?php echo $fTestComments; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td style="width:10%">&nbsp;<?php echo $fDescription; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><a href='autoOamEditRunDesc.php?runId=<?php echo $fRunId; ?>&db=<?php echo $db; ?>'>Edit</a></td>
</tr>

<?php
}
$i++;
}
?>

<script type="text/javascript">
function refresh()
{
    window.location='stack.php?user=' + document.getElementById('userInput').value;
}
</script>
</table>
</form>
</body>
</html>

