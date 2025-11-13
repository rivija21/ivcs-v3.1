<?php
/*
 * This script fetches data from the 'traffic_violations' table
 * and returns it as JSON for the violations.html page.
 * calld by violations.html 
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
    // Return empty array on error so the frontend doesn't break
    echo json_encode([]);
    exit();
}

// Fetch the 50 most recent data from units.
$sql = "SELECT 
            vehicle_plate, 
            data_time, 
            latitude, 
            longitude, 
            speed, 
            rpm, 
            throttle, 
            brake_status, 
            headlight_state, 
            signal_light_state 
        FROM traffic_violations 
        ORDER BY data_time DESC 
        LIMIT 50";

$result = $conn->query($sql);

$violations = [];

if ($result && $result->num_rows > 0) {
    // Fetch all results into an associative array
    while($row = $result->fetch_assoc()) {
        $violations[] = $row;
    }
}

// --- Output JSON ---
echo json_encode($violations);

$conn->close();

?>
