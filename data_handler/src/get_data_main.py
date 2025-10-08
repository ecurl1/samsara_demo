#!/usr/bin/env python3
"""Main entry point for the script."""

from __future__ import annotations
from src.api_handler import URLRequestHandler, VehicleAPIResponse, SensorListAPIResponse, TemperatureSensorAPIResponse, DoorSensorAPIResponse
from src.constants import SamsaraEndpoints
from src.data_model import Vehicle, Sensor
from constants import LOCAL_TIME_SERIES_STORAGE_FILE
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import asyncio

def get_vehicle_data() -> VehicleAPIResponse | None:
    """Helper function to grab fleet vehicle data."""
    vehicle_response = asyncio.run(URLRequestHandler.fetch_data_httpx(suffix=SamsaraEndpoints.FLEET, asset_suffix=SamsaraEndpoints.VEHICLES))
    if vehicle_response is not None:
        return VehicleAPIResponse.from_json(vehicle_response)
    else:
        print("[API VEHICLE WRAPPER] Response empty.")
        return None

def get_sensor_list() -> SensorListAPIResponse | None:
    """Helper function to get sensor list."""
    sensor_response = asyncio.run(URLRequestHandler.get_sensor_list())
    if sensor_response is not None:
        return SensorListAPIResponse.from_json(sensor_response)
    else:
        print("[API SENSOR WRAPPER] Response empty.")
        return None
    
def get_sensor_data(
        sensor_list_response: SensorListAPIResponse
    ) -> list[TemperatureSensorAPIResponse | DoorSensorAPIResponse] | None:
    """Helper function to get sensor data."""
    return asyncio.run(URLRequestHandler.get_sensor_data(sensor_list_response))

def convert_data_model_to_timeseries(vehicle_data:Vehicle, sensor_list: list[Sensor], sensor_data_list) -> pd.DataFrame:
    """Convert extracted responses into a consumable format for local data storage."""
    # create some dictionaries from the extracted vehicle and sensor data responses
    vehicle_data_to_save = {
        "Make": vehicle_data.make,
        "Model": vehicle_data.model,
        "Year": vehicle_data.year,
        "Gateway SN": vehicle_data.externalIds.serial
    }

    sensor_list_data_to_save = {}
    for i, (sensor, sensor_data) in enumerate(zip(sensor_list, sensor_data_list)):
        sensor_list_data_to_save[f"Sensor {i} ID"] = sensor.id,
        sensor_list_data_to_save[f"Sensor {i} Name"] = sensor.name,
        sensor_list_data_to_save[f"Sensor {i} MAC"] = sensor.mac_address,
    
        if isinstance(sensor_data, TemperatureSensorAPIResponse):
            sensor_list_data_to_save[f"Sensor {i} Type"] = "Temperature",
            sensor_list_data_to_save["Ambient Temp."] = sensor_data.sensors[0].ambient_temperature * 0.001 * (9/5) + 32 # millicelcius -> Farenheit
            sensor_list_data_to_save["Ambient Temp. Timestamp"] = sensor_data.sensors[0].ambient_temperature_time.strftime("%Y-%m-%d %H:%M")
        else:
            sensor_list_data_to_save[f"Sensor {i} Type"] = "Door",
            sensor_list_data_to_save["Door State"] = sensor_data.sensors[0].door_closed
            sensor_list_data_to_save["Door State Timestamp"] = sensor_data.sensors[0].door_status_time.strftime("%Y-%m-%d %H:%M")

    # convert data dictionaries into dataframes, concatenate and return
    vehicle_df = pd.DataFrame([vehicle_data_to_save])
    sensor_df = pd.DataFrame([sensor_list_data_to_save])

    final_row_df = pd.concat([vehicle_df, sensor_df], axis=1, ignore_index=False)
    final_row_df.sort_index(inplace=True)

    return final_row_df

def update_data_warehouse(row_data_df: pd.DataFrame) -> None:
    """Create and/or save timeseries data to storage."""

    if not os.path.exists(LOCAL_TIME_SERIES_STORAGE_FILE):
        row_data_df.to_parquet(LOCAL_TIME_SERIES_STORAGE_FILE, engine='pyarrow', index=True, compression="snappy")
    else:
        timeseries_df = pd.read_parquet(LOCAL_TIME_SERIES_STORAGE_FILE, dtype_backend="pyarrow")
        timeseries_df_updated = pd.concat([timeseries_df, row_data_df])
        timeseries_df_updated.sort_index(inplace=True)
        for col in timeseries_df_updated.select_dtypes(include=["object"]).columns:
            timeseries_df_updated[col] = timeseries_df_updated[col].astype(str)
        timeseries_df_updated.to_parquet(LOCAL_TIME_SERIES_STORAGE_FILE, engine='pyarrow', index=True, compression="snappy")
    print(f"[MAIN] Local timeseries updated.")

def main():
    """Main script to pull info down from the cloud."""


    # pull vehicle info, sensor data
    vehicle_data = get_vehicle_data()
    if vehicle_data is None:
        raise ValueError("[MAIN] Empty response from vehicle wrapper.")
    vehicle_data = vehicle_data.data[0]
    sensor_list = get_sensor_list()
    if sensor_list is None:
        raise ValueError("[MAIN] Empty response from sensor list wrapper.")
    sensor_data_list = get_sensor_data(sensor_list)
    if sensor_data_list is None:
        raise ValueError("[MAIN] Empty response from sensor data wrapper.")

    # convert extracted data models into a row we can add to timeseries data
    data_row_df = convert_data_model_to_timeseries(vehicle_data, sensor_list.sensors, sensor_data_list)
    # well use a local file as a data warehouse
    update_data_warehouse(data_row_df)



if __name__ == "__main__":
    main()
