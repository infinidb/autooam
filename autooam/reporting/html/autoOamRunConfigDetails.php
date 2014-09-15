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
$configId=$_GET["configId"];
$db = $_GET["db"];
if (strpos($db, 'unit') > 0) {
    $prev2="autoOamRuns.php?unit=1";
}
else {
    $prev2="autoOamRuns.php";
}
$prev="autoOamRunDetails.php?runId=" . $runId . "&db=" . $db;
mysql_select_db ($db);
$query="call list_runConfig_details($runId, $configId)"; 
$result=mysql_query($query)
or die(mysql_error());

$num=mysql_numrows($result);

mysql_close();
?>
<body>
<a href='<?php echo $prev2; ?>'>AutoOam Nightly Results</a> > <a href='<?php echo $prev; ?>'>Run Details</a> > <a href='<?php $_SERVER['PATH_INFO'] ?>'>Run Config Details</a>
<br>
<br>
<!-- <table border="1" cellspacing="2" cellpadding="2"> -->
<table border="1" cellspacing="1" cellpadding="2">
<tr>
<th align=left>Run</th>
<th align=left>Seq</th>
<th align=left>Name</th>
<th align=left>Description</th>
<th align=left>Status</th>
<th aligh=left>Time</th>
<th aligh=left>Comments</th>
<th aligh=left>Edit</th>
</tr>

<?php
$i=0;
while ($i < $num) {

$fRunId=mysql_result($result,$i,"runId");
$fSequence=mysql_result($result,$i,"runConfigId");
$fName=mysql_result($result,$i,"name");
// TODO: Add a runConfigTestId column instead of using name.
$fDescription=mysql_result($result,$i,"description");
$fRunTime=mysql_result($result,$i,"runTime");
$fComments=mysql_result($result,$i,"comments");

/* Make any numeric testComments link to Bugzilla. */
$comments=explode(",", $fComments);
foreach ($comments as &$x) {
    if (is_numeric($x)) {
        $fComments=str_replace($x, "<a href='http://srvengcm1.calpont.com/bugzilla/show_bug.cgi?id=" . $x ."'>" . $x . "</a>", $fComments);
    }
}

$fStatus=mysql_result($result,$i,"status");
if ($fStatus == "Passed") {
    $fStatus="<font color=green><b>Passed</b></font>";
}
elseif ($fStatus == "Failed") {
    $fStatus="<font color=red><b>Failed</b></font>";
}

?>

<tr>
<td><?php echo $fRunId; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fSequence; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fName; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fDescription; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fStatus; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fRunTime; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><?php echo $fComments; ?>&nbsp;&nbsp;&nbsp;</font></td>
<td><a href='autoOamEditTestComments.php?runId=<?php echo $fRunId; ?>&db=<?php echo $db; ?>&runConfigId=<?php echo $fSequence ?>&name=<?php echo $fName ?>'>Edit</a></td>
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

