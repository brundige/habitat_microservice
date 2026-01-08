# this file orchestrates the data coming from the sensors and sends it to the server
import time
import os
import requests
from requests.exceptions import RequestException
from models.tank import Tank
import asyncio
import logging

logger = logging.getLogger(__name__)

# configure the REST endpoint (override via environment)
SERVER_API_URL = os.getenv("SERVER_API_URL", "http://localhost:8000/api/readings")

# Store the polling task so we can cancel it on shutdown
_polling_task = None

# Sample tank configuration - can be expanded to read from database
TANKS = {
    1: {
        "name": "Tank 1 (Leopard Gecko)",
        "target_temp": 29.0,
        "target_humidity": 40.0,
        "reptile_species": "Leopard Gecko"
    },
    2: {
        "name": "Tank 2 (Bearded Dragon)",
        "target_temp": 35.0,
        "target_humidity": 30.0,
        "reptile_species": "Bearded Dragon"
    },
    3: {
        "name": "Tank 3 (Ball Python)",
        "target_temp": 29.0,
        "target_humidity": 60.0,
        "reptile_species": "Ball Python"
    }
}

async def initialize():
    """Start the sensor polling loop in the background."""
    global _polling_task
    try:
        # Start polling sensors asynchronously
        _polling_task = asyncio.create_task(poll_sensors_async())
        logger.info("Sensor polling loop started for %d tanks", len(TANKS))
    except Exception as e:
        logger.error("Failed to initialize sensor interface: %s", str(e))
        raise


async def poll_sensors_async():
    """Continuously poll sensors and send data to server."""
    while True:
        try:
            # Poll all configured tanks
            for tank_id, tank_config in TANKS.items():
                tank = Tank(
                    id=tank_id,
                    temp=tank_config["target_temp"],
                    humidity=tank_config["target_humidity"],
                    light=True
                )
                data = tank.get_habitat_readings()
                update_server(data)
                logger.info(
                    f"Tank {tank_id} ({tank_config['name']}): "
                    f"temp={data['temp']}°C, humidity={data['humidity']}%, light={data['light']}"
                )
        except Exception as e:
            logger.error("Error polling sensors: %s", str(e))

        await asyncio.sleep(5)  # Poll every 5 seconds


async def cleanup():
    """Cleanup sensor interface on shutdown."""
    global _polling_task
    if _polling_task:
        _polling_task.cancel()
        try:
            await _polling_task
        except asyncio.CancelledError:
            pass
    logger.info("Sensor interface cleanup complete")


def update_server(data):
    """Send sensor data to the REST API instead of writing directly to the DB."""
    try:
        resp = requests.post(SERVER_API_URL, json=data, timeout=5)
        resp.raise_for_status()
        logger.debug(f"Successfully posted sensor data to server: {resp.status_code}")
    except RequestException as e:
        # simple single retry
        try:
            resp = requests.post(SERVER_API_URL, json=data, timeout=5)
            resp.raise_for_status()
            logger.debug(f"Posted sensor data to server on retry: {resp.status_code}")
        except RequestException as e2:
            logger.error(f"Failed to post sensor data to server: {e2}")
