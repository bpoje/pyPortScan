<?php
$servername = "localhost";
$username = "readScan";
$password = "Pass-54321";
$dbname = "portScan";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
echo "Connected successfully" . "<br>";

echo "<style>table, th, td {border: 1px solid black;}</style>";

$sql = "SELECT idlog, idNode, idTimestamp, port, isOpen FROM log";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    echo "<table style='width:100%'>";
    echo "<tr>
            <th>idlog</th>
            <th>idNode</th>
            <th>idTimestamp</th>
            <th>port</th>
            <th>isOpen</th>
          </tr>";

    // output data of each row
    while($row = $result->fetch_assoc()) {
      echo "<tr>";

      echo
      "<td>" . $row["idlog"] . "</td>" .
      "<td>" . $row["idNode"] . "</td>" .
      "<td>" . $row["idTimestamp"] . "</td>" .
      "<td>" . $row["port"] . "</td>" .
      "<td>" . $row["isOpen"] . "</td>";

      echo "</tr>";
    }
    echo "</table>";
} else {
    echo "0 results";
}
$conn->close();

?>
