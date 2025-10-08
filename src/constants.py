#!/usr/bin/env python3
"""This file will hold constants used in the demo."""

from typing import Final

# location where the api token is loaded from local to container
API_TOKEN_LOCATION: Final = "/demo/secrets/api_token.txt"
LOCAL_TIME_SERIES_STORAGE: Final = "/demo/secrets/sensor_data.parquet"
# some type definitions for different samsara api integrations
class SamsaraEndpoints:
    FLEET: str = "fleet"
    V1: str = "v1"
    VEHICLES: str = "vehicles"
    SENSORS: str = "sensors"
    LIST: str = "list"
    TEMPERATUER: str = "temperature"
    DOOR: str = "door"

# keeping track of serial nums here for ease of access
class SensorSerialNums:
    TEMP: str = "W7NP-RJ8-6VE"
    DOOR: str = "WM5D-K78-KN7"


