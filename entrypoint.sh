#!/bin/bash
# entrypoint.sh - Start both API and sensor simulator

# Start the API in the background
uvicorn server.app:app --host 0.0.0.0 --port 8000 &

# Wait for the API to be ready
sleep 5

# Start the sensor simulator
python sensor_interface.py

