"""
Cache Helper Utility

Provides functions to read cached results from blob storage.
Phase 3 Requirement: Use cached data instead of recalculating.
"""

import json
import logging
from azure.storage.blob import BlobServiceClient


def get_cached_results(connect_str, container_name="datasets", cache_blob_name="cached_results.json"):
    """
    Retrieves cached calculation results from blob storage.

    Returns:
        dict: Cached results or None if cache doesn't exist
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=cache_blob_name
        )

        # Download cache
        cache_data = blob_client.download_blob().readall()
        cache_results = json.loads(cache_data)

        logging.info("✅ Successfully loaded cached results")
        return cache_results

    except Exception as e:
        logging.warning(f"⚠️ Cache not found or invalid: {str(e)}")
        return None
