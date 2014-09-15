<?php
$con = mysql_connect('localhost','root','',false,65536);
$runId=$_POST["runId"];
$db=$_POST["db"];
$description=$_POST["description"];
mysql_select_db ($db);
if (strpos($db, 'unit') > 0) {
    $prev="autoOamRuns.php?unit=1";
}
else {
    $prev="autoOamRuns.php";
}
$query="update run set description='" . $description . "' where runId = " . $runId;
$result=mysql_query($query)
or die(mysql_error());

mysql_close();

header('Location:' . $prev);
?>
