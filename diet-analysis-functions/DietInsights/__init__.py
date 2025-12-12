import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.cache_helper import get_cached_results

def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()

    try:
        # Get connection string from environment variable (local.settings.json)
        connect_str = os.environ.get("AzureStorageConnection")
        if not connect_str:
            raise ValueError("AzureStorageConnection not found in environment variables")

        container_name = "datasets"

        # PHASE 3: Try to get data from cache first
        cache = get_cached_results(connect_str, container_name)

        if cache and "insights" in cache:
            # Use cached data (FAST!)
            result = cache["insights"]["diet_insights"]
        else:
            # Fallback: Calculate from cleaned CSV if cache not available
            blob_name = "All_Diets_cleaned.csv"
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
            blob_data = blob_client.download_blob().readall()
            usecols = ["Diet_type", "Protein(g)", "Carbs(g)", "Fat(g)"]
            dtypes = {
                "Diet_type": "category",
                "Protein(g)": "float32",
                "Carbs(g)": "float32",
                "Fat(g)": "float32"
            }
            df = pd.read_csv(io.BytesIO(blob_data), usecols=usecols, dtype=dtypes)
            avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().reset_index()
            result = avg_macros.to_dict(orient="records")
        elapsed = round(time.time() - start_time, 3)

        # Return JSON result
        return func.HttpResponse(
            json.dumps({
                "elapsed_seconds": elapsed,
                "diet_insights": result
            }, indent=4),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
