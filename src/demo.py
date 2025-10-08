#!/usr/bin/env python3
"""Main entry point for the script."""

from __future__ import annotations
from src.api_handler import get_api_token, URLRequestHandler, APIVehicleResponseWrapper
from src.constants import SamsaraAssetSuffix, SamsaraEndpoints
import asyncio






def get_vehicle_data() -> APIVehicleResponseWrapper | None:
    """Helper function to grab fleet vehicle data."""
    vehicle_dict = asyncio.run(URLRequestHandler.fetch_data_httpx(suffix=SamsaraEndpoints.FLEET, asset_suffix=SamsaraAssetSuffix.VEHICLES))
    if vehicle_dict is not None:
        return APIVehicleResponseWrapper.from_json(vehicle_dict)
    else:
        print("[API VEHICLE WRAPPER] Response empty.")
        return None
