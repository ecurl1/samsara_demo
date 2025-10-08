# this file handles loading api
import os
from src import constants

def get_api_token() -> str | None:
    """Helper to get secret API token."""
    try:
        with open(constants.API_TOKEN_LOCATION, "r") as token:
            return token.read().strip()
    except FileNotFoundError as exc:
        print(f"[SETUP ERROR]:{exc} Could not find API token at {constants.API_TOKEN_LOCATION}")
        return None
