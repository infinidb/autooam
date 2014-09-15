<html>
<head>
<meta http-equiv="refresh" content="60" >
</head>
<?php
header('Cache-Control: no-cache, no-store, must-revalidate'); // HTTP 1.1. 
header('Pragma: no-cache'); // HTTP 1.0. 
header('Expires: 0'); // Proxies.
$con = mysql_connect('localhost','root','',false,65536);
$runId=$_GET["runId"];
$db = $_GET["db"];
mysql_select_db ($db);
if (strpos($db, 'unit') > 0) {
    $prev="autoOamRuns.php?unit=1";
}
else {
    $prev="autoOamRuns.php";
}
$query="call get_runConfigs($runId)"; 
$result=mysql_query($query)
or die(mysql_error());

$num=mysql_numrows($result);

mysql_close();
?>
<body>
<a href='<?php echo $prev; ?>'>AutoOam Nightly Results</a> > <a href='<?php $_SERVER['PATH_INFO'] ?>'> Run Details</a>
<br>
<br>
<!-- <table border="1" cellspacing="2" cellpadding="2"> -->
<table border="1" cellspacing="1" cellpadding="2">
<tr>
<th align=left>ID</font></th>
<th align=left>Cluster Name</font></th>
<th align=left>Cluster ID</font></th>
<th align=left>Ver</font></th>
<th align=left>EM Ver</font></th>
<th align=left>Box Type</font></th>
<th align=left>Config Name</font></th>
<th align=left>User</font></th>
<th align=left>Dup</font></th>
<th align=left>Bin</font></th>
<th align=left>Storage</font></th>
<th align=left>PM Query</font></th>
<th align=left>Start</font></th>
<th align=left>Time</font></th>
<th align=left>Status</font></th>
<th align=left>Passed</font></th>
<th align=left>Failed</font></th>
<th align=left>Bad Starts</font></th>
<th align=left>Test Failures</font></th>
<th align=left>Test Comments</font></th>
</tr>

<?php
$i=0;
while ($i < $num) {

$fRunId=mysql_result($result,$i,"runId");
$fSequence=mysql_result($result,$i,"runConfigId");
$fName=mysql_result($result,$i,"name");
$fClusterId=mysql_result($result,$i,"clusterId");
$fIdbVersion=mysql_result($result,$i,"idbVersion");
$fEmVersion=mysql_result($result,$i,"emVersion");
$fBoxType=mysql_result($result,$i,"boxType");
$fConfigName=mysql_result($result,$i,"configName");
$fStart=mysql_result($result,$i,"start");
$fRunTime=mysql_result($result,$i,"runTime");
$fStatus=mysql_result($result,$i,"status");
$fPassed=mysql_result($result,$i,"passed");
$fFailed=mysql_result($result,$i,"failed");
$fStartupFailed=mysql_result($result,$i,"startupFailed");
$fUser=mysql_result($result,$i,"idbUser");
$fDatDup=mysql_result($result,$i,"datDup");
$fBinary=mysql_result($result,$i,"binaryInstallation");
$fTestFails=mysql_result($result,$i,"testFails");
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

$fStorage=mysql_result($result,$i,"storage");
$fPMQuery=mysql_result($result,$i,"pm_query");
if ($fStatus == "Passed") {
    $fStatus="<font color=green><b>Passed</b></font>";
}
elseif ($fStatus == "Failed") {
    $fStatus="<font color=red><b>Failed</b></font>";
}

?>

<tr>
<td><a href='autoOamRunConfigDetails.php?runId=<?php echo $runId; ?>&configId=<?php echo $fSequence; ?>&db=<?php echo $db; ?>'><?php echo $fRunId ?>.<?php echo $fSequence; ?></a>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fName; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fClusterId; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fIdbVersion; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fEmVersion; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fBoxType; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fConfigName;  ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fUser;  ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fDatDup;  ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fBinary;  ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fStorage;  ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fPMQuery;  ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fStart; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fRunTime; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fStatus; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fPassed; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fFailed; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fStartupFailed; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fTestFails; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fTestComments; ?>&nbsp;&nbsp;&nbsp;</font></td>
</tr>

<?php
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

