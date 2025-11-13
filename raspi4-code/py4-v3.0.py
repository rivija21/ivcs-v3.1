import serial
import pynmea2
import requests
import time
import json
from mpu6050 import mpu6050
from datetime import datetime
import os  
import can  

# --- Configuration ---
VEHICLE_PLATE = "IVCS_UNIT_001" 
SERVER_IP = "10.180.231.153"
LOCATION_URL = f"http://{SERVER_IP}/ivcs/update_location.php"
VIOLATION_URL = f"http://{SERVER_IP}/ivcs/add_violation.php"

# --- Sensor Configuration ---
SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 9600
MPU_ADDR = 0x68
ACCEL_THRESHOLD_G = 5.0 


CAN_INTERFACE = 'can0'
# Standard OBD-II bitrate. Change if vehicle bus is different (e.g., 250000)
CAN_BITRATE = 500000 

def initialize_can(interface):
    """
    Brings up the specified CAN interface.
    """
    print(f"Initializing CAN interface {interface}...")
    try:
        # Bring up the CAN interface
        os.system(f'sudo ip link set {interface} down') # Ensure it's down first
        os.system(f'sudo ip link set {interface} type can bitrate {CAN_BITRATE}')
        os.system(f'sudo ip link set {interface} up')
        
        # Initialize the CAN bus object
        bus = can.interface.Bus(channel=interface, bustype='socketcan')
        print("CAN bus connection successful.")
        return bus
    except Exception as e:
        print(f"CRITICAL: Failed to initialize CAN bus: {e}")
        print(f"Please ensure SPI is enabled, dtoverlay is set, and '{interface}' exists.")
        return None

def poll_can_data(bus, current_data):
    """
    Non-blockingly reads all pending CAN messages and updates the data store.
    This is where you will add your reverse-engineering logic.
    """
    if not bus:
        return current_data # Return last known data if bus failed

    try:
        msg = bus.recv(timeout=0) # Non-blocking read
        while msg:
            # --- START: Your Reverse-Engineering Logic Goes Here ---
            
            # You need to find the message IDs (msg.arbitration_id)
            # and data bytes (msg.data) for your vehicle.
            # Printing the message is the first step to finding them.
            
            # Uncomment this line to see all CAN messages (will be spammy!)
            # print(f"CAN RX: ID={hex(msg.arbitration_id)} DLC={msg.dlc} Data={msg.data.hex()}")

            # Example logic (replace with your findings):
            # if msg.arbitration_id == 0x1A5: # Example ID
            #     # Example: RPM is bytes 0 and 1
            #     # (Data[0] * 256 + Data[1]) / 4
            #     current_data['rpm'] = ((msg.data[0] << 8) | msg.data[1]) / 4
            #     
            #     # Example: Speed is byte 2 (km/h)
            #     current_data['speed'] = msg.data[2]

            # elif msg.arbitration_id == 0x2B1: # Example ID
            #     # Example: Fuel level is byte 4 (%)
            #     current_data['fuel_level'] = msg.data[4] * 0.4
            #     
            #     # Example: Throttle position is byte 1
            #     current_data['throttle'] = msg.data[1] * 0.4

            # --- END: Your Reverse-Engineering Logic ---
            
            msg = bus.recv(timeout=0) # Read next message in buffer
            
    except Exception as e:
        print(f"Error reading CAN: {e}")
    
    # Return the (potentially updated) data dictionary
    return current_data

def log_violation(plate, lat, lng, acc_x, acc_y, can_data): # Added can_data
    """
    Sends a detailed violation report to the add_violation.php script,
    now including all available CAN data.
    """
    print(f"---! VIOLATION DETECTED !---")
    print(f"Abnormal G-Force: X={acc_x:.2f}, Y={acc_y:.2f}")
    
    try:
        now = datetime.now()
        data_time = now.strftime('%Y-%m-%d %H:%M:%S')

        # Create the base data payload
        base_payload = {
            'vehicle_plate': plate,
            'data_time': data_time,
            'latitude': lat,
            'longitude': lng,
            'acc_x': acc_x,
            'acc_y': acc_y,
        }
        # Merge base payload with CAN data, which may contain None values (added by the php automatically)
        violation_payload = {**base_payload, **can_data}
        
        # Send the POST request to log the violation
        response = requests.post(VIOLATION_URL, data=violation_payload, timeout=5)
        print(f"Violation Logged. Server Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error logging violation: {e}")

# --- Main Program ---
print(f"--- IVCS Device {VEHICLE_PLATE} ---")
print(f"Connecting to GPS on {SERIAL_PORT}...")
print(f"Initializing MPU6050 at address {hex(MPU_ADDR)}...")

can_data_store = {
    "rpm": None,
    "speed": None,
    "headlight_state": None,
    "signal_light_state": None,
    "inside_temp": None,
    "humidity": None,
    "fuel_level": None,
    "throttle": None,
    "brake_status": None,
} #upgradable- air-bag status, oil temp, door locks, shutter positions, etc.

try:
    # Initialize sensors
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=5)
    mpu = mpu6050(MPU_ADDR)
    can_bus = initialize_can(CAN_INTERFACE) # --- NEW ---
    
    if not can_bus:
        print("CRITICAL: CAN bus failed to start. Exiting.")

        pass 

    print("GPS and MPU6050 Connection Successful.")
    print(f"Sending location updates to {LOCATION_URL}")
    print(f"Monitoring for G-force events > {ACCEL_THRESHOLD_G} G")
    print(f"Monitoring CAN bus {CAN_INTERFACE} for data...")

    while True:
        try:
            # This keeps the can_data_store as up-to-date as possible
            can_data_store = poll_can_data(can_bus, can_data_store)

            # --- Original GPS Logic ---
            line = ser.readline().decode('ascii', errors='replace')
            
            if line.startswith('$GPGGA') or line.startswith('$GNGGA'): 
                msg = pynmea2.parse(line)
                
                if msg.latitude != 0.0 and msg.longitude != 0.0:
                    lat = msg.latitude
                    lng = msg.longitude
                    
                    try:
                        location_data = {"lat": lat, "lng": lng}
                        with open('last_location.json', 'w') as f:
                            json.dump(location_data, f)
                    except Exception as e:
                        print(f"Error writing last_location.json: {e}")
                    # (Optional: Print GPS fix)
                    # print(f"GPS Fix: Lat={lat}, Lng={lng}")

                    location_payload = {
                        "device_id": VEHICLE_PLATE, 
                        "lat": lat,
                        "lng": lng
                    }
                    try:
                        response = requests.post(LOCATION_URL, json=location_payload, timeout=5)
                        # (Optional: Print location update)
                        # print(f"Location Sent. Server Response: {response.text}")
                    
                    except requests.exceptions.RequestException as e:
                        print(f"Error sending location: {e}")

                    # --- 2. Check for Violation (Modified) ---
                    try:
                        accel_data = mpu.get_accel_data()
                        acc_x = accel_data['x']
                        acc_y = accel_data['y']

                        if abs(acc_x) > ACCEL_THRESHOLD_G or abs(acc_y) > ACCEL_THRESHOLD_G:
                            # --- MODIFIED: Pass the can_data_store ---
                            log_violation(VEHICLE_PLATE, lat, lng, acc_x, acc_y, can_data_store)
                            
                            time.sleep(3) # Pause to prevent spamming

                    except Exception as e:
                        print(f"Error reading MPU6050: {e}")

                # else:
                    # print("Waiting for GPS fix...")
            
            # Short delay in the main loop (was 1s, 0.1s may be more responsive)
            time.sleep(0.1) 

        except pynmea2.ParseError as e:
            pass
        except Exception as e:
            print(f"An error occurred in the loop: {e}")

except serial.SerialException as e:
    print(f"CRITICAL: Error opening serial port: {e}")
except IOError as e:
    print(f"CRITICAL: Error initializing MPU6050: {e}")
    print("Please check I2C connection and address.")
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
    
    # --- NEW: Shutdown CAN interface ---
    if 'can_bus' in locals() and can_bus:
        os.system(f'sudo ip link set {CAN_INTERFACE} down')
        print("CAN interface shut down.")