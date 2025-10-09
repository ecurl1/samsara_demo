#!/usr/bin/env python3

import plotly.graph_objects as go
from plotly.graph_objects import Figure
from src.constants import TimeseriesKeys
from constants import LOCAL_TIME_SERIES_STORAGE_FILE
import pandas as pd
import numpy as np

def request_time_range_data(start_time: str, end_time: str) -> pd.DataFrame:
    command = [
        
    ]

def clean_str(text: str) -> str:
    """Removes artifacts from json serialization."""
    chars_to_remove = ", '\"[]"
    translation_table = str.maketrans('', '', chars_to_remove)
    return text.translate(translation_table)

def parse_header_info(timeseries_df: pd.DataFrame) -> dict:
    """Parse some header info from the timeseries data."""
    
    # get vehicle data
    header_info = {
    TimeseriesKeys.MAKE: timeseries_df[TimeseriesKeys.MAKE].iloc[0],
    TimeseriesKeys.MODEL: timeseries_df[TimeseriesKeys.MODEL].iloc[0],
    TimeseriesKeys.YEAR: timeseries_df[TimeseriesKeys.YEAR].iloc[0],
    }
    # get sensor data
    num_sensors = sum(1 for col in timeseries_df.columns if "Sensor" in col and "ID" in col)
    header_info["Sensors"] = {}
    for i in range(num_sensors):
        sensor_dict={
            "Sensor ID": clean_str(str(timeseries_df[f"Sensor {i} ID"].iloc[0])),
            "Serial Number": clean_str(timeseries_df[f"Sensor {i} Name"].iloc[0]),
            "MAC Address": clean_str(timeseries_df[f"Sensor {i} MAC"].iloc[0]),
        }
        header_info["Sensors"][clean_str(timeseries_df[f"Sensor {i} Type"].iloc[0])] = sensor_dict
        
    return header_info

def load_data() -> pd.DataFrame:
    """Get the locally stored timeseries data from fetch data events."""
    timeseries_df = pd.read_parquet(LOCAL_TIME_SERIES_STORAGE_FILE)
    
    # ensure correct dtypes
    timeseries_df[TimeseriesKeys.AMBIENT_TEMP_TIMESTAMP] = pd.to_datetime(timeseries_df[TimeseriesKeys.AMBIENT_TEMP_TIMESTAMP])
    timeseries_df[TimeseriesKeys.DOOR_STATE_TIMESTAMP] = pd.to_datetime(timeseries_df[TimeseriesKeys.DOOR_STATE_TIMESTAMP])
    timeseries_df[TimeseriesKeys.AMBIENT_TEMP] = pd.to_numeric(timeseries_df[TimeseriesKeys.AMBIENT_TEMP], errors='coerce')
    timeseries_df[TimeseriesKeys.DOOR_STATE] = pd.to_numeric(timeseries_df[TimeseriesKeys.DOOR_STATE], errors='coerce')

    print("[DATAWAREHOUSE] Loading timeseries data...")
    return timeseries_df

def plot_timeseries(timeseries_df: pd.DataFrame, data_key: str, timestamp_key: str) -> Figure:
    """Plot timeseries data onto interactive plot."""

    # slice appropriate data
    df_plot = timeseries_df[[timestamp_key, data_key]].copy()
    df_plot = df_plot.set_index(timestamp_key)
    df_aggregated = df_plot.groupby(level=0)[data_key].mean().reset_index()
    
    # create the plot using the simple names
    x_data = df_aggregated[timestamp_key].tolist()
    y_data = df_aggregated[data_key].tolist()
    trace = go.Scatter(
                  x=x_data,
                  y=y_data,
                  mode='lines+markers',
                  name=data_key,
    )

    # create the figure
    x_axis_title = "Time"
    y_axis_title = f"{TimeseriesKeys.AMBIENT_TEMP} (°F)" if "Temp" in data_key else data_key
    fig = go.Figure(data=[trace])
    fig.update_layout(title=f"{data_key} Over Time")
    fig.update_xaxes(title_text=x_axis_title)
    fig.update_yaxes(title_text=y_axis_title)
    fig.update_xaxes(rangeslider_visible=True)

    return fig