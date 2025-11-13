<?php
// pull data unto the database
// Database connection details
$servername = "localhost";
$username = "root"; 
$password = "";     
$dbname = "ivcs";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// Check if data is coming via POST request
if ($_SERVER["REQUEST_METHOD"] == "POST") {
  // Get data from the POST request
  $event_type = $_POST['event_type'];
  $latitude = $_POST['latitude'];
  $longitude = $_POST['longitude'];

  // Use prepared statements to prevent SQL injection
  $stmt = $conn->prepare("INSERT INTO alerts (latitude, longitude, event_type) VALUES (?, ?, ?)");
  $stmt->bind_param("dds", $latitude, $longitude, $event_type);

  // Execute the statement and send a response
  if ($stmt->execute()) {
    echo json_encode(["status" => "success", "message" => "Alert logged."]);
  } else {
    echo json_encode(["status" => "error", "message" => "Failed to log alert."]);
  }

  $stmt->close();
} else {
  echo json_encode(["status" => "error", "message" => "Invalid request method."]);
}

$conn->close();
?>