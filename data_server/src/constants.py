#!/usr/bin/env python3
"""Define some constants for the server app."""

from typing import Final

# where the timeseries data is mounted in the container
LOCAL_TIME_SERIES_STORAGE_FILE: Final = "/data_server/data/sensor_data.parquet"
LOCAL_HISTORY_TIME_SERIES_STORAGE_FILE: Final = "/data_server/data/sensor_history_data.parquet"

# flask constants
TEMPLATE_FOLDER: Final = "/data_server/src/templates"
HOST_BASE_DIR: Final = "/home/ecurl/samsara_demo"

# define constants for data keys
class TimeseriesKeys:
    AMBIENT_TEMP = "Ambient Temp."
    AMBIENT_TEMP_TIMESTAMP = "Ambient Temp. Timestamp"
    DOOR_STATE = "Door State"
    DOOR_STATE_TIMESTAMP = "Door State Timestamp"
    MAKE = "Make"
    MODEL = "Model"
    YEAR = "Year"
    GATEWAY_SN = "Gateway SN"
    SENSOR_0_ID = "Sensor 0 ID"
    SENSOR_0_NAME = "Sensor 0 Name"
    SENSOR_0_MAC = "Sensor 0 MAC"
    SENSOR_0_TYPE = "Sensor 0 Type"
    SENSOR_1_ID = "Sensor 1 ID"
    SENSOR_1_NAME = "Sensor 1 Name"
    SENSOR_1_MAC = "Sensor 1 MAC"
    SENSOR_1_TYPE = "Sensor 1 Type"