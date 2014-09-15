<?php
$con = mysql_connect('localhost','root','',false,65536);
$runId=$_POST["runId"];
$comments=$_POST["comments"];
$runConfigId=$_POST["runConfigId"];
$name=$_POST["name"];
$db=$_POST["db"];
$prev="autoOamRunConfigDetails.php?db=" .$db . "&runId=" . $runId . "&configId=" . $runConfigId . "&name=" .$name;

mysql_select_db ($db);
$query="call edit_runConfigTest($runId, $runConfigId, '$name', '$comments')";
$result=mysql_query($query)
or die(mysql_error());
mysql_close();

header('Location:' . $prev);
?>
