#!/usr/bin/env python3
"""This file holds data models for the Vehicles, requests."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# === Vehicle Request Response Data Models ===
class TemperatureSensor(BaseModel):
    id: str
    name: str
    mac: str

class Area(BaseModel):
    position: str
    temperature_sensor: list[TemperatureSensor] = Field(alias="temperatureSensors")

class SensorConfiguration(BaseModel):
    areas: list[Area]

class Gateway(BaseModel):
    serial: str
    model: str

class ExternalIds(BaseModel):
    serial: str = Field(alias="samsara.serial")
    model: str = Field(alias="samsara.vin")

class Attribute(BaseModel):
    id: str
    name: str
    stringValues: list[str]

class Vehicle(BaseModel):
    id: str
    name: str
    make: str
    model: str
    year: str
    serial: str
    vin: str
    licensePlate: Optional[str] = ""
    notes: Optional[str] = ""
    harshAccelerationSettingType: Optional[str] = ""
    vehicleRegulationMode: str
    createdAtTime: str
    updatedAtTime: str

    attributes: list[Attribute]
    externalIds: ExternalIds
    gateway: Gateway
    sensorConfiguration: SensorConfiguration

# === Sensor Request Response Data Models ===
class Sensor(BaseModel):
    id: int
    name: str
    mac_address: str = Field(alias="macAddress")

class GroupedSensor(BaseModel):
    id: int
    name: str
    vehicle_id: int = Field(alias="vehicleId")

class GroupedTemperatureSensor(GroupedSensor):
    ambient_temperature: int = Field(alias="ambientTemperature")
    ambient_temperature_time: datetime = Field(alias="ambientTemperatureTime")

class GroupedDoorSensor(GroupedSensor):
    door_closed: bool = Field(alias="doorClosed")
    door_status_time: datetime = Field(alias="doorStatusTime")

