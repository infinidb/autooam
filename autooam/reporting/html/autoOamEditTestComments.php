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
$runConfigId=$_GET["runConfigId"];
$name=$_GET["name"];
$db = $_GET["db"];
if (strpos($db, 'unit') > 0) {
    $prev3="autoOamRuns.php?unit=1";
}
else {
    $prev3="autoOamRuns.php";
}
$prev2="autoOamRunDetails.php?runId=" . $runId . "&db=" . $db;
$prev="autoOamRunConfigDetails.php?db=" . $db . "&runId=" . $runId . "&configId=" . $runConfigId . "&name=" . $name;
mysql_select_db ($db);
$query="call get_runConfigTest($runId, $runConfigId, '$name')"; 
$result=mysql_query($query)
or die(mysql_error());

$num=mysql_numrows($result);

mysql_close();
?>
<body>
<a href='<?php echo $prev3; ?>'>AutoOam Nightly Results</a> > <a href='<?php echo $prev2; ?>'>Run Details</a> > <a href='<?php echo $prev; ?>'>Run Config Details</a> > <a href='<?php $_SERVER['PATH_INFO'] ?>'>Edit Test Comments</a>
<br>
<br>

<?php
$i=0;
while ($i < $num) {

$fRunId=mysql_result($result,$i,"runId");
$fRunConfigId=mysql_result($result,$i,"runConfigId");
$fName=mysql_result($result,$i,"name");
$fRunTime=mysql_result($result,$i,"runTime");
$fComments=mysql_result($result,$i,"comments");
$fStatus=mysql_result($result,$i,"status");
if ($fStatus == "Passed") {
    $fStatus="<font color=green><b>Passed</b></font>";
}
elseif ($fStatus == "Failed") {
    $fStatus="<font color=red><b>Failed</b></font>";
}

?>
<form action="autoOamSaveTestDescription.php" method="post" id="form1">
<input id="db" name="db" type="hidden" value="<?php echo $db; ?>"/>
<input id="runId" name="runId" type="hidden" value="<?php echo $fRunId; ?>"/>
<input id="runConfigId" name="runConfigId" type="hidden" value="<?php echo $fRunConfigId; ?>"/>
<input id="name" name="name" type="hidden" value="<?php echo $fName; ?>"/>
<table>
<tr><td>Run ID:</td><td><?php echo $fRunId; ?></td></tr>
<tr><td>Seq:</td><td><?php echo $fRunConfigId; ?></td></tr>
<tr><td>Name:</td><td><?php echo $fName; ?></td></tr>
<tr><td>Status:</td><td><?php echo $fStatus; ?></td></tr>
<tr><td>Run Time:</td><td><?php echo $fRunTime; ?></td></tr>
<tr><td>Comments:</td><td><input id="comments" name="comments" size=100 value="<?php echo $fComments; ?>"</input></td></tr>
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

