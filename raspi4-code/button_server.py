import asyncio
import websockets
import json
from gpiozero import Button  # <-- We import Button from the new library
import time

# --- Configuration ---
BUTTON_PIN = 17  # GPIO pin (BCM numbering)
WEBSOCKET_PORT = 8765

connected_clients = set()

# --- Setup button with gpiozero ---
# This automatically handles pull-up resistors and debouncing!
# It assumes your button connects GPIO 17 to GND.
try:
    button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.3)
    print(f"GPIO Pin {BUTTON_PIN} setup. Waiting for button press...")
except Exception as e:
    print(f"--- FAILED TO INITIALIZE GPIO PIN {BUTTON_PIN} ---")
    print("Error: ", e)
    exit()


def on_button_press():    
    print(f"--- BUTTON PRESS DETECTED on pin {BUTTON_PIN} ---")

    # 1. Read location
    try:
        with open('last_location.json', 'r') as f:
            location = json.load(f)
        print(f"Read location: {location}")
    except Exception as e:
        print(f"Could not read last_location.json: {e}. Using default.")
        location = {"lat": 0, "lng": 0} # Send default

    # 2. Create message
    message = json.dumps({
        "event_type": "landslide_button_press",
        "latitude": location["lat"],
        "longitude": location["lng"]
    })

    # 3. Send message to all browsers
    if connected_clients:
        print(f"Sending message to {len(connected_clients)} clients: {message}")
        # Schedule the broadcast to run on the main asyncio loop
        asyncio.run_coroutine_threadsafe(
            broadcast(message),
            asyncio.get_event_loop()
        )
    else:
        print("Button pressed, but no clients are connected.")

# --- Assign our function to the button's "when_pressed" event ---
# The gpiozero library handles all the looping/listening in the background.
button.when_pressed = on_button_press

async def broadcast(message):
    """Sends a message to all connected clients."""
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

async def register(websocket):
    """Registers a new client connection."""
    print(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        print(f"Client disconnected: {websocket.remote_address}")
        connected_clients.remove(websocket)

async def main():
    """Runs the WebSocket server."""
    print(f"Starting WebSocket server on ws://0.0.0.0:{WEBSOCKET_PORT}")
    async with websockets.serve(register, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Runs forever

if __name__ == "__main__":
    try:
        # Run the asyncio main loop
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram stopped.")