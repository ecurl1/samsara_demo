#!/usr/bin/env python3
"""This file handles loading api token from the container."""
from __future__ import annotations
from src.data_model import Vehicle, Sensor, GroupedSensor, GroupedTemperatureSensor, GroupedDoorSensor
from src.constants import SamsaraEndpoints, SensorSerialNums, API_TOKEN_LOCATION
from pydantic import BaseModel, Field
from typing import Any
import httpx
import json

 # helper funciton to load secret API token
def get_api_token() -> str | None:
    """Helper to get secret API token."""
    try:
        with open(API_TOKEN_LOCATION, "r", encoding="ASCII") as token:
            return token.read().strip()
    except FileNotFoundError as exc:
        print(f"[SETUP ERROR]:{exc} Could not find API token at {API_TOKEN_LOCATION}")
        return None

# === Request Handler ===
class URLRequestHandler:
    """Main handler for getting url requests."""
    SAMSARA_BASE_URL: str = "https://api.samsara.com"

    @classmethod
    def get_request_url(cls, end_point_list: list[str]) -> str:
        """Construct request url from suffix and asset names.

        Args: 
            suffix: e.g., 'fleet'.
            asset_suffix: e.g, 'vehicles'.
        Returns:
            request URL with configured fields.
        """
        return f"{cls.SAMSARA_BASE_URL}/{'/'.join(end_point_list)}"

    @classmethod
    def get_authorization_header(cls) -> dict[str, str]:
        """Get authorization header for the request.

        Returns:
            dictionary containing head and authorization token.
        """
        api_token = get_api_token()
        header = {
            "Authorization": f"Bearer {api_token}",
        }
        return header

    @classmethod
    async def fetch_data_httpx(cls, suffix: str, asset_suffix: str) -> dict[str, Any] | None:
        """Fetch data given suffix and asset.
        
        Args: 
            suffix: e.g., 'fleet'.
            asset_suffix: e.g, 'vehicles'.
        Returns:
            json of requested data, if successful.
        """
        # get url and authorization header
        request_url = URLRequestHandler.get_request_url(end_point_list=[suffix, asset_suffix])
        authorization_header = URLRequestHandler.get_authorization_header()
        # use httpx to connect with Samsara api
        async with httpx.AsyncClient(headers=authorization_header) as client:
            try:
                response = await client.get(request_url)
                response.raise_for_status()
                print(f"[REQUEST] Status: {request_url}={response.status_code}")
                return response.json()
            except httpx.HTTPStatusError as status_error:
                print(f"[REQUEST] HTTP error occured: {status_error}")
            except httpx.RequestError as request_error:
                print(f"[REQUEST] Error occured during request: {request_error}")
        
    @classmethod
    async def get_sensor_list(cls) -> dict[str, Any] | None:
        """Grab all available sensors.
        
        Returns:
            json of requested data, if successful.
        """
        # get url and authorization header
        request_url = URLRequestHandler.get_request_url(
            [SamsaraEndpoints.V1, SamsaraEndpoints.SENSORS, SamsaraEndpoints.LIST]
        )
        authorization_header = URLRequestHandler.get_authorization_header()
        async with httpx.AsyncClient(headers=authorization_header) as client:
            try:
                response = await client.post(request_url)
                response.raise_for_status()
                print(f"[REQUEST] Status: {request_url}={response.status_code}")
                return response.json()
            except httpx.HTTPStatusError as status_error:
                print(f"[REQUEST] HTTP error occured: {status_error}")
            except httpx.RequestError as request_error:
                print(f"[REQUEST] Error occured during request: {request_error}")

    @classmethod
    async def get_sensor_data(
        cls, sensor_list_response: SensorListAPIResponse
        ) -> list[TemperatureSensorAPIResponse | DoorSensorAPIResponse] | None:
        """Grab all available sensor data.
        
        Returns:
            json of requested data, if successful.
        """

        sensor_endpoints, sensor_ids = sensor_list_response.parse_sensor_list_response()

        sensor_data_responses: list[Any] = []
        for sensor_endpoint, sensor_id in zip(sensor_endpoints, sensor_ids):
            # get url and authorization header
            request_url = URLRequestHandler.get_request_url(
                [SamsaraEndpoints.V1, SamsaraEndpoints.SENSORS, sensor_endpoint],
            )
            payload = {
                "sensors": [sensor_id]
            }
            authorization_header = URLRequestHandler.get_authorization_header()
            async with httpx.AsyncClient(headers=authorization_header) as client:
                try:
                    response = await client.post(request_url, json=payload)
                    response.raise_for_status()
                    print(f"[REQUEST] Status: {request_url}={response.status_code}")
                    sensor_data_responses.append(response.json())
                except httpx.HTTPStatusError as status_error:
                    print(f"[REQUEST] HTTP error occured: {status_error}")
                    sensor_data_responses.append(None)
                except httpx.RequestError as request_error:
                    print(f"[REQUEST] Error occured during request: {request_error}")
                    sensor_data_responses.append(None)
        
        output: list[Any] = []
        for response, sensor_endpoint in zip(sensor_data_responses, sensor_endpoints):
            if response is not None:
                if sensor_endpoint == SamsaraEndpoints.DOOR:
                    output.append(DoorSensorAPIResponse.from_json(response))
                else:
                    output.append(TemperatureSensorAPIResponse.from_json(response))
            else:
                print(f"[API SENSOR WRAPPER] Response empty for type {sensor_endpoint}.")

        return output


# === API Response Data Models ===
class BaseAPIResponse(BaseModel):
    """Base wrapper for API response"""
    @classmethod
    def from_json(cls, json_data: dict[str, Any]):
        return cls.model_validate(json_data)


class VehicleAPIResponse(BaseAPIResponse):
    """Wrapper for vehicle request response."""
    data: list[Vehicle]
    pagination: dict[str, Any]

    @classmethod
    def from_json(cls, json_data: dict[str, Any]):
        return cls.model_validate(json_data)


class SensorListAPIResponse(BaseAPIResponse):
    """Wrapper for sensor request response."""
    sensors: list[Sensor]

    def parse_sensor_list_response(self):
        """Helper to determine sensor id and what type based on serial number."""
        sensor_serial_nums: list[str] = [sensor.name for sensor in self.sensors]
        sensor_ids: list[int] = [sensor.id for sensor in self.sensors]
        sensor_endpoints = [
            SamsaraEndpoints.DOOR if (
                sensor_id == SensorSerialNums.DOOR
            ) else SamsaraEndpoints.TEMPERATUER for sensor_id in sensor_serial_nums
        ]
        return sensor_endpoints, sensor_ids

class DoorSensorAPIResponse(BaseAPIResponse):
    """Wrapper for sensor request response."""
    group_id: int = Field(alias="groupId")
    sensors: list[GroupedDoorSensor]

class TemperatureSensorAPIResponse(BaseAPIResponse):
    """Wrapper for sensor request response."""
    group_id: int = Field(alias="groupId")
    sensors: list[GroupedTemperatureSensor]
