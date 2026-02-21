"""Climate Trace API client for the Emissions Sources dashboard."""

import requests

BASE_URL = "https://api.climatetrace.org/v7"

SECTORS = [
    "mineral-extraction",
    "fossil-fuel-operations",
    "transportation",
    "power",
    "fluorinated-gases",
    "forestry-and-land-use",
    "buildings",
    "manufacturing",
    "waste",
    "agriculture",
]


def get_gases():
    """Fetch all available gas types."""
    try:
        response = requests.get(f"{BASE_URL}/definitions/gases", timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching gases: {e}")
        return ["co2e_100yr", "co2e_20yr", "co2", "ch4", "n2o"]


def get_continents():
    """Fetch all available continents."""
    try:
        response = requests.get(f"{BASE_URL}/definitions/continents", timeout=15)
        response.raise_for_status()
        return [c for c in response.json() if c not in ("Unknown", "Antarctica")]
    except requests.RequestException as e:
        print(f"Error fetching continents: {e}")
        return ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"]


def get_sources(year=2024, gas="co2e_100yr", sectors=None, limit=100):
    """Fetch ranked emission sources.

    Args:
        year: Emissions year (min 2021, default 2024).
        gas: Gas type (default co2e_100yr).
        sectors: List of sector strings or None for all.
        limit: Max results to return.

    Returns:
        List of source summary dicts.
    """
    params = {"year": year, "gas": gas, "limit": limit}
    if sectors:
        params["sectors"] = ",".join(sectors)

    try:
        response = requests.get(f"{BASE_URL}/sources", params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching sources: {e}")
        return []


def get_emissions(year=2024, gas="co2e_100yr", continent=None, sector=None):
    """Fetch aggregated monthly emissions data.

    Args:
        year: Emissions year (min 2015, default 2024).
        gas: Gas type (default co2e_100yr).
        continent: Continent name or None for global.
        sector: List of sector strings or None for all.

    Returns:
        Dict with location, totals, sectors, and subsectors data.
    """
    params = {"year": year, "gas": gas}
    if continent:
        params["continent"] = continent
    if sector:
        params["sector"] = ",".join(sector)

    try:
        response = requests.get(
            f"{BASE_URL}/sources/emissions", params=params, timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching emissions: {e}")
        return None
