#!/usr/bin/env python3
"""Main entry point for the script."""

from __future__ import annotations
import os
import pandas as pd
import asyncio
import argparse
from typing import Any
from src.api_handler import (
    URLRequestHandler, 
    VehicleAPIResponse, 
    SensorListAPIResponse, 
    TemperatureSensorAPIResponse, 
    DoorSensorAPIResponse, 
    SensorHistoryAPIResponse
)
from src.constants import SamsaraEndpoints, SensorSerialNums
from src.data_model import Vehicle, Sensor
from constants import LOCAL_TIME_SERIES_STORAGE_FILE, LOCAL_HISTORY_TIME_SERIES_STORAGE_FILE



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
        sensor_list_response: SensorListAPIResponse,
    ) -> list[TemperatureSensorAPIResponse | DoorSensorAPIResponse] | None:
    """Helper function to get sensor data."""
    return asyncio.run(URLRequestHandler.get_sensor_data(sensor_list_response))

def get_sensor_history_data(sensor_list_response: SensorListAPIResponse, start_time:str, end_time:str) -> dict[str, Any] | None | None:
    """helper to grab sensor history information for sensors in list."""
    sensor_history_response = asyncio.run(
        URLRequestHandler.get_sensor_history(
        sensor_list_response, start_time=start_time, end_time=end_time
        )
    )
    return sensor_history_response

def convert_data_model_to_timeseries(vehicle_data:Vehicle, sensor_list: list[Sensor], sensor_data_list) -> pd.DataFrame:
    """Convert extracted responses into a consumable format for local data storage."""
    # create some dictionaries from the extracted vehicle and sensor data responses
    vehicle_data_to_save = {
        "Make": vehicle_data.make,
        "Model": vehicle_data.model,
        "Year": vehicle_data.year,
        "Gateway SN": vehicle_data.externalIds.serial
    }
    # create sensor dict
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

def convert_history_to_timeseries(vehicle_data:Vehicle, sensor_list: list[Sensor], sensor_history_data: SensorHistoryAPIResponse) -> pd.DataFrame:
    """Convert extracted responses into a consumable format for local data storage."""
    # create some dictionaries from the extracted vehicle and sensor data responses - repeat for each timestamp
    len_timestamps = len(sensor_history_data.results)
    vehicle_data_to_save = {
        "Make": [vehicle_data.make for _ in range(len_timestamps)],
        "Model": [vehicle_data.model for _ in range(len_timestamps)],
        "Year": [vehicle_data.year for _ in range(len_timestamps)],
        "Gateway SN": [vehicle_data.externalIds.serial for _ in range(len_timestamps)],
    }
    # extract sensor data
    sensor_list_data_to_save = {}
    for i, sensor in enumerate(sensor_list):
        sensor_list_data_to_save[f"Sensor {i} ID"] = [sensor.id for _ in range(len_timestamps)]
        sensor_list_data_to_save[f"Sensor {i} Name"] = [sensor.name for _ in range(len_timestamps)]
        sensor_list_data_to_save[f"Sensor {i} MAC"] = [sensor.mac_address for _ in range(len_timestamps)]
        sensor_list_data_to_save[f"Sensor {i} Type"] = ["Temperature" if sensor.name == SensorSerialNums.TEMP else "Door" for _ in range(len_timestamps)]
        if sensor.name == SensorSerialNums.TEMP:
            sensor_list_data_to_save["Ambient Temp."] = [result.values[i] * 0.001 * (9/5) + 32 for result in sensor_history_data.results] # millicelcius -> Farenheit
            sensor_list_data_to_save["Ambient Temp. Timestamp"] = [result.time_ms.strftime("%Y-%m-%d %H:%M") for result in sensor_history_data.results]
        else:
            sensor_list_data_to_save["Door State"] = [result.values[i] for result in sensor_history_data.results]
            sensor_list_data_to_save["Door State Timestamp"] = [result.time_ms.strftime("%Y-%m-%d %H:%M") for result in sensor_history_data.results]
    
    # convert data dictionaries into dataframes, concatenate and return
    vehicle_df = pd.DataFrame(vehicle_data_to_save)
    sensor_df = pd.DataFrame(sensor_list_data_to_save)

    final_row_df = pd.concat([vehicle_df, sensor_df], axis=1, ignore_index=False)
    final_row_df.sort_index(inplace=True)

    return final_row_df        
        
def update_data_warehouse(row_data_df: pd.DataFrame, save_path: str = LOCAL_TIME_SERIES_STORAGE_FILE) -> None:
    """Create and/or save timeseries data to storage."""

    if not os.path.exists(save_path) or save_path == LOCAL_HISTORY_TIME_SERIES_STORAGE_FILE:
        row_data_df.to_parquet(save_path, engine='pyarrow', index=True, compression="snappy")
    else:
        timeseries_df = pd.read_parquet(save_path, dtype_backend="pyarrow")
        timeseries_df_updated = pd.concat([timeseries_df, row_data_df])
        timeseries_df_updated.sort_index(inplace=True)
        for col in timeseries_df_updated.select_dtypes(include=["object"]).columns:
            timeseries_df_updated[col] = timeseries_df_updated[col].astype(str)
        timeseries_df_updated.to_parquet(save_path, engine='pyarrow', index=True, compression="snappy")
    print(f"[MAIN] Local timeseries updated.")

def update_data_warehouse_from_time_range(start_time: str, end_time: str) -> None:
    """Update the local data warehouse from a specified time range."""
    
    # get vehicle info and sensor info
    vehicle_data = get_vehicle_data()
    if vehicle_data is None:
        raise ValueError("[MAIN] Empty response from vehicle wrapper.")
    vehicle_data = vehicle_data.data[0]
    sensor_list = get_sensor_list()
    if sensor_list is None:
        raise ValueError("[MAIN] Empty response from sensor list wrapper.")
    
    # get sensor data for time range
    time_series_values = get_sensor_history_data(sensor_list, start_time, end_time)
    if time_series_values is not None:
        wrapped_time_series_values = SensorHistoryAPIResponse.from_json(time_series_values)
    else:
        print("[API SENSOR HISTORY WRAPPER] Response empty.")
        return None
    
    # convert extracted data models into table
    timeseries_df = convert_history_to_timeseries(vehicle_data, sensor_list.sensors, wrapped_time_series_values)
    update_data_warehouse(timeseries_df, LOCAL_HISTORY_TIME_SERIES_STORAGE_FILE)

def main():
    """Main script to pull info down from the cloud."""

    # get command line args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start-time',
        type=str,
        default=None,
    )
    parser.add_argument(
        '--end-time',
        type=str,
        default=None,
    )
    args = parser.parse_args()
    start_time = args.start_time
    end_time = args.end_time
    
    # just use start/end time from GUI to determine run mode for now
    if start_time is not None and end_time is not None:
        # use history function to update data warehouse
        update_data_warehouse_from_time_range(start_time, end_time)
    else:
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
    """execute only if run as a script"""
    main()
