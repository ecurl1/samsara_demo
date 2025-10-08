#!/usr/bin/env python3
"""Define some constants for the server app."""

from typing import Final

# where the timeseries data is mounted in the container
LOCAL_TIME_SERIES_STORAGE_FILE: Final = "/data_server/data/sensor_data.parquet"

# flask constants
TEMPLATE_FOLDER: Final = "/data_server/src/templates"

# define constants for data keys
class TimeseriesKeys:
    AMBIENT_TEMP = "Ambient Temp."
    AMBIENT_TEMP_TIMESTAMP = "Ambient Temp. Timestamp"
    DOOR_STATE = "Door State"
    DOOR_STATE_TIMESTAMP = "Door State Timestamp"