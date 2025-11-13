<?php
header('Content-Type: application/json');
// pulls data unto the map
// called by index.html 
// --- Database Connection ---
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "ivcs";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// --- Fetch Data ---
// only select devices that have updated in the last 2 minutes (120 seconds)
// This way, disconnected devices will automatically disappear from the map.
$sql = "SELECT device_id, lat, lng FROM device_locations 
        WHERE last_updated > (NOW() - INTERVAL 120 SECOND)";

$result = $conn->query($sql);

$locations = array();

if ($result->num_rows > 0) {
    // Loop through each row and add it to our $locations array
    while($row = $result->fetch_assoc()) {
        // We cast lat and lng to floats just to be safe
        $row['lat'] = (float)$row['lat'];
        $row['lng'] = (float)$row['lng'];
        $locations[] = $row;
    }
}

// --- Output as JSON ---
echo json_encode($locations);

$conn->close();
?>