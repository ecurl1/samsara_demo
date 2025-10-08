#!/usr/bin/env python3
"""This file handles loading api token from the container."""

from src import constants
from src.data_model import Vehicle
from pydantic import BaseModel
from typing import Any
import httpx
import json


def get_api_token() -> str | None:
    """Helper to get secret API token."""
    try:
        with open(constants.API_TOKEN_LOCATION, "r", encoding="ASCII") as token:
            return token.read().strip()
    except FileNotFoundError as exc:
        print(f"[SETUP ERROR]:{exc} Could not find API token at {constants.API_TOKEN_LOCATION}")
        return None

class URLRequestHandler:
    """Main handler for getting url requests."""
    SAMSARA_BASE_URL: str = "https://api.samsara.com"

    @classmethod
    def get_request_url(cls, suffix: str, asset_suffix: str) -> str:
        """Construct request url from suffix and asset names.

        Args: 
            suffix: e.g., 'fleet'.
            asset_suffix: e.g, 'vehicles'.
        Returns:
            request URL with configured fields.
        """
        return f"{cls.SAMSARA_BASE_URL}/{suffix}/{asset_suffix}"

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
            json of requested data, if succesful.
        """
        # get url and authorization header
        request_url = URLRequestHandler.get_request_url(suffix=suffix, asset_suffix=asset_suffix)
        request_header = URLRequestHandler.get_authorization_header()
        # use httpx to connect with Samsara api
        async with httpx.AsyncClient(headers=request_header) as client:
            try:
                response = await client.get(request_url)
                response.raise_for_status()
                print(f"[REQUEST] Status: {response.status_code}")
                return response.json()
            except httpx.HTTPStatusError as status_error:
                print(f"[REQUEST] HTTP error occured: {status_error}")
            except httpx.RequestError as request_error:
                print(f"[REQUEST] Error occured during request: {request_error}")
        

class APIVehicleResponseWrapper(BaseModel):
    """Wrapper for vehicle request response."""
    data: list[Vehicle]
    pagination: dict[str, Any]

    @classmethod
    def from_json(cls, json_data: dict[str, Any]):
        return cls.model_validate(json_data)