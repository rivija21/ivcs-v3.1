<?php
// Set the content type to JSON for our response
header('Content-Type: application/json');

// --- Configuration ---
$servername = "localhost";
$username = "root"; 
$password = "";     
$dbname = "ivcs";

// Python Model Configuration ---
$python_executable = " C:\\Users\\USER\\miniconda3\\envs\\inceptionv3\\python.exe"; #no dedicated env!!!
$prediction_script = "C:\\xampp\\htdocs\\ivcs\\predict.py"; 

// function to send a structured JSON response ---
function send_json_response($status, $event_type, $message) {
    echo json_encode([
        "status" => $status,
        "event_type" => $event_type, // "car_crash"
        "message" => $message
    ]);
    exit; // Stop the script
}
// Validate Request ---
if ($_SERVER["REQUEST_METHOD"] != "POST" || empty($_FILES['landslide_image'])) {
  send_json_response("error", null, "Invalid request or no image uploaded.");
}

$latitude = $_POST['latitude'] ?? '0';
$longitude = $_POST['longitude'] ?? '0';
$image_file = $_FILES['landslide_image'];

// Handle File Upload ---
if ($image_file['error'] !== UPLOAD_ERR_OK) {
    send_json_response("error", null, "File upload error code: " . $image_file['error']);
}
$upload_dir = 'uploads/'; 
if (!is_dir($upload_dir)) {
    mkdir($upload_dir, 0777, true);
}

// Create a unique file path
$image_path = $upload_dir . uniqid('event-') . '-' . basename($image_file['name']);

if (!move_uploaded_file($image_file['tmp_name'], $image_path)) {
    send_json_response("error", null, "Failed to save uploaded file. Check directory permissions.");
}

// // Execute Python CNN Model ---
// $full_image_path = realpath($image_path); //this returned an err :(

$safe_image_path = escapeshellarg($image_path); 
$command = $python_executable . " " . $prediction_script . " " . $safe_image_path . " 2>&1";
$output = shell_exec($command);

// Process Model Output ---
if ($output === null) {
    unlink($image_path); // Cleanup
    send_json_response("error", null, "Failed to execute model. Check PHP 'shell_exec' permissions and Python executable path.");
    // error_log("Model Output: " . $output);
}

// The output from python will be the predicted class name
$predicted_class = trim($output);

// Define your model's possible outputs
$valid_classes = ['landslide', 'car_crash', 'road_maintenance', 'normal_road'];

if (!in_array($predicted_class, $valid_classes)) {
    unlink($image_path); // Cleanup
    send_json_response("error", $predicted_class, "Model returned an unknown class: " . htmlspecialchars($predicted_class));
}

// Cleanup Uploaded Image ---
unlink($image_path);

// Log to Database (if it's an event) ---
if ($predicted_class == 'normal_road') {
    // This was not an incident, so we don't log it.
    send_json_response("ignored", $predicted_class, "Image analyzed as 'Normal Road'. No alert logged.");
}

// Log it to the database if it's not a normal road
$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
  send_json_response("error", $predicted_class, "Database connection failed: " . $conn->connect_error);
}

// Format the class name for the database (e.g., "car_crash" -> "Car Crash")
$event_type_db = ucwords(str_replace('_', ' ', $predicted_class));

$stmt = $conn->prepare("INSERT INTO alerts (latitude, longitude, event_type) VALUES (?, ?, ?)");
if (!$stmt) {
    $conn->close();
    send_json_response("error", $predicted_class, "Database prepare failed: " . $conn->error);
}

$stmt->bind_param("dds", $latitude, $longitude, $event_type_db);

if ($stmt->execute()) {
    $stmt->close();
    $conn->close();
    send_json_response("success", $predicted_class, "Event logged successfully as: " . $event_type_db);
} else {
    // Database insert failed
    $stmt->close();
    $conn->close();
    send_json_response("error", $predicted_class, "Model predicted event, but failed to log to database.");
}

?>