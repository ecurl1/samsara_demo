#!/usr/bin/env python3
"""This file will hold constants used in the demo."""

from typing import Final

# location where the api token is loaded from local to container
API_TOKEN_LOCATION: Final = "/demo/secrets/api_token.txt"

# some type definitions for different samsara api integrations
class SamsaraEndpoints:
    FLEET: str = "fleet"
class SamsaraAssetSuffix:
    VEHICLES: str = "vehicles"