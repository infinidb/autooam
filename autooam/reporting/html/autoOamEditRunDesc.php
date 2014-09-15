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
$query="call get_run($runId)"; 
$result=mysql_query($query)
or die(mysql_error());

$num=mysql_numrows($result);

mysql_close();
?>
<body>
<a href='<?php echo $prev; ?>'>AutoOam Nightly Results</a> > <a href='<?php $_SERVER['PATH_INFO'] ?>'> Edit Run Description</a>
<br>
<br>

<?php
$i=0;
while ($i < $num) {

$fRunId=mysql_result($result,$i,"runId");
$fVersion=mysql_result($result,$i,"idbVersions");
$fStart=mysql_result($result,$i,"start");
$fRunTime=mysql_result($result,$i,"runTime");
$fPassed=mysql_result($result,$i,"passed");
$fFailed=mysql_result($result,$i,"failed");
$fHost=mysql_result($result,$i,"host");
$fDescription=mysql_result($result,$i,"description");
$fStatus=mysql_result($result,$i,"status");
if ($fStatus == "Passed") {
    $fStatus="<font color=green><b>Passed</b></font>";
}
elseif ($fStatus == "Failed") {
    $fStatus="<font color=red><b>Failed</b></font>";
}

?>
<form action="autoOamRunSaveDescription.php" method="post" id="form1">
<input id="db" name="db" type="hidden" value="<?php echo $db; ?>"/>
<input id="runId" name="runId" type="hidden" value="<?php echo $runId; ?>"/>
<table>
<tr><td>Run ID:</td><td><?php echo $fRunId; ?></td></tr>
<tr><td>Host:</td><td><?php echo $fHost; ?></td></tr>
<tr><td>Status:</td><td><?php echo $fStatus; ?></td></tr>
<tr><td>Start:</td><td><?php echo $fStart; ?></td></tr>
<tr><td>Runt Time:</td><td><?php echo $fRunTime; ?></td></tr>
<tr><td>Passed:</td><td><?php echo $fPassed; ?></td></tr>
<tr><td>Failed:</td><td><?php echo $fFailed; ?></td></tr>
<tr><td>Version:</td><td><?php echo $fVersion; ?></td></tr>
<tr><td>Description:</td><td><input id="description" name="description" size=100 value="<?php echo $fDescription; ?>"</input></td></tr>
</table>
<input type="button" value="Submit" id="commit" onClick="document.getElementById('form1').submit();">
<input type="button" value="Cancel" id="cancel" onClick="window.location.href='<?php echo $prev; ?>'">
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
</form>
</body>
</html>

