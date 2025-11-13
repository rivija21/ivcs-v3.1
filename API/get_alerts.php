<?php
//pull alerts from the database and return to the alert.html page as JSON

header('Content-Type: application/json'); // Tell the browser this is JSON data

$servername = "localhost";
$username = "root";
$password = "";
$dbname = "ivcs";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// Select all alerts, ordered by the newest first
$sql = "SELECT id, event_time, latitude, longitude, event_type FROM alerts ORDER BY event_time DESC";
$result = $conn->query($sql);

$alerts = array();

if ($result->num_rows > 0) {
  // Fetch data into an array
  while($row = $result->fetch_assoc()) {
    $alerts[] = $row;
  }
}

// Encode the array as JSON and send it
echo json_encode($alerts);

$conn->close();
?>