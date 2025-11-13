# Intelligent Vehicular Communication System (IVCS)

**Project by: Chenul, Rivija, Vihara**
**Supervisor: Dr. Saniru Gayan**

> This project (v3.1) proposes an intelligent system to enhance road safety and emergency response efficiency. It features a portable, in-vehicle device and a central cloud backend.

---

## 🎯 Problem Statement

Traffic congestion and the inability of modern traffic systems to prioritize emergency vehicles lead to preventable delays and loss of life. Furthermore, existing navigation systems lack critical, real-time data on road barricades, accidents, or maintenance. This project aims to solve these issues with a centralized, data-driven solution.

## ✨ Key Features

* **Emergency Vehicle Pass-Through:** Allows ambulances to anonymously transmit real-time location data, enabling the system to communicate with traffic lights and clear a path.
* **Road Barricade Reporting:** A system for reporting road obstructions like landslides or maintenance, which can be integrated with services like Google Maps.
* **Vehicle Incident Database:** Automatically detects and uploads a 30-second pre- and post-event data log (CAN, GPS, sensor readings) to a secure database upon detecting a potential accident (e.g., sudden G-force spike).

---

## 🛠️ System Architecture

The project is divided into three main subsystems:

1.  **Subsystem-A: Emergency vehicle pass-through**
    * Ambulance drivers can pre-upload their route via a GUI.
    * The server handles pass-by access at traffic lights based on proximity (100m) and a first-come, first-served logic.

2.  **Subsystem-B: Report about landslides, road maintenance**
    * Utilizes an IoT input module with dedicated buttons for different incident types (e.g., "Accident," "Landslide").
    * Authorized personnel can send an instant, human-verified alert to the central server.

3.  **Subsystem-C: Maintaining a database of vehicle status**
    * Uses a CAN transceiver to extract vehicle data (speed, RPM, brake status, airbag deployment, etc.).
    * An accelerometer and pressure gauge detect a "possible contingency" and trigger an data upload to a time-series database.

---

## ⚙️ Hardware (IVCS Onboard Device)

* **Microcontroller:** Raspberry Pi 4
* **GPS:** NEO-M8N module + active antenna
* **Cellular:** SIM7600C series module
* **CAN:** MCP2515 + TJA1050 transceiver
* **Sensors:**
    * Accelerometer / Gyroscope
    * Temperature / Humidity sensors
    * Pressure gauge
* **Input:** Push buttons

## ☁️ Software & Backend

* **Cloud Backend (V21):**
    * API Gateway
    * Processing Engine
    * Secure portal for authorities
* **Networking:**
    * Prototype uses WiFi (2.4GHz) with HTTP POST requests (JSON headers).
    * APIs are secured against common attacks like SQL injection.
* **Database:**
    * Main Geospatial Database
    * Time-Series Database (for Subsystem-C)

---

## 🔮 Future Work (Upgradables)

* **Priority System:** Upgrade Subsystem-A to assign priority levels when multiple emergency vehicles approach a junction.
* **Public Reporting:** Upgrade Subsystem-B to allow public reporting, verified using a CNN to analyze photographic proof.
* **Alternative Routes:** Provide alternative routes to drivers when alerts are triggered on their path.
* **CAN Data:** Reverse engineer CAN data for specific vehicle brands to standardize data extraction.
