<?php
/*
 * add_violation.php
 * This script receives data from IVCS device (via POST)
 * and inserts it into the database.
 * listens for data from the IVCS device 
 */

// --- Database Configuration ---
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "ivcs";

// ---Header ---
header('Content-Type: application/json');

// ---connection ---
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    echo json_encode(['status' => 'error', 'message' => 'Connection failed: ' . $conn->connect_error]);
    exit();
}

// --- Get Data from POST Request ---
// TO DO --> validation and sanitation as needed for production.
$vehicle_plate = $_POST['vehicle_plate'] ?? null;
$data_time = $_POST['data_time'] ?? null;
$latitude = $_POST['latitude'] ?? null;
$longitude = $_POST['longitude'] ?? null;
$acc_x = $_POST['acc_x'] ?? null;
$acc_y = $_POST['acc_y'] ?? null;
$rpm = $_POST['rpm'] ?? null;
$speed = $_POST['speed'] ?? null;
$headlight_state = $_POST['headlight_state'] ?? null;
$signal_light_state = $_POST['signal_light_state'] ?? null;
$inside_temp = $_POST['inside_temp'] ?? null;
$humidity = $_POST['humidity'] ?? null;
$fuel_level = $_POST['fuel_level'] ?? null;
$throttle = $_POST['throttle'] ?? null;
$brake_status = $_POST['brake_status'] ?? null;

// --- Basic Validation ---
if (empty($vehicle_plate) || empty($data_time) || empty($latitude) || empty($longitude)) {
    echo json_encode(['status' => 'error', 'message' => 'Missing required fields (plate, time, location).']);
    exit();
}

// --- Prepare and Bind SQL Statement ---
$stmt = $conn->prepare(
    "INSERT INTO traffic_violations (
        vehicle_plate, data_time, latitude, longitude, acc_x, acc_y, rpm, speed, 
        headlight_state, signal_light_state, inside_temp, humidity, fuel_level, throttle, brake_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
);

if ($stmt === false) {
    echo json_encode(['status' => 'error', 'message' => 'Failed to prepare statement: ' . $conn->error]);
    exit();
}

// Bind parameters
$stmt->bind_param(
    "ssddddiiisssddi",
    $vehicle_plate,
    $data_time,
    $latitude,
    $longitude,
    $acc_x,
    $acc_y,
    $rpm,
    $speed,
    $headlight_state,
    $signal_light_state,
    $inside_temp,
    $humidity,
    $fuel_level,
    $throttle,
    $brake_status
);

// --- Execute and Close ---
if ($stmt->execute()) {
    echo json_encode(['status' => 'success', 'message' => 'New violation record created successfully.']);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Execute failed: ' . $stmt->error]);
}

$stmt->close();
$conn->close();

?>
