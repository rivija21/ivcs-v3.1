<?php
// updates data unto the database
// called by the Raspberry Pi devices
// --- Database Connection ---
$servername = "localhost";
$username = "root"; // Default XAMPP username
$password = "";     // Default XAMPP password
$dbname = "ivcs";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// --- Get JSON data from the Pi ---
// The Pi will send data as JSON
$json_data = file_get_contents('php://input'); // grabber
$data = json_decode($json_data);

// Check if data is valid
if (isset($data->device_id) && isset($data->lat) && isset($data->lng)) {
    
    $device_id = $data->device_id;
    $lat = $data->lat;
    $lng = $data->lng;

    
    // tries to INSERT a new row.
    // If a row with the same PRIMARY KEY (device_id) already exists,
    // UPDATE that existing row instead.
    $sql = "INSERT INTO device_locations (device_id, lat, lng) 
            VALUES (?, ?, ?)
            ON DUPLICATE KEY UPDATE 
            lat = ?, lng = ?, last_updated = CURRENT_TIMESTAMP";

    $stmt = $conn->prepare($sql);
    // string, double, double, double, double
    $stmt->bind_param("sdddd", $device_id, $lat, $lng, $lat, $lng);

    if ($stmt->execute()) {
        echo json_encode(["status" => "success", "message" => "Location updated for " . $device_id]);
    } else {
        echo json_encode(["status" => "error", "message" => "Execute failed: " . $stmt->error]);
    }

    $stmt->close();

} else {
    echo json_encode(["status" => "error", "message" => "Invalid data received."]);
}

$conn->close();
?>