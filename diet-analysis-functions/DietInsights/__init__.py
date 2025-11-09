import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os
import time

def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()

    try:
        # Get connection string from environment variable (local.settings.json)
        connect_str = os.environ.get("AzureStorageConnection")
        if not connect_str:
            raise ValueError("AzureStorageConnection not found in environment variables")

        container_name = "datasets"
        blob_name = "All_Diets.csv"

        # Connect to Azurite or Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
        blob_data = blob_client.download_blob().readall()

        # Read only necessary columns with optimized data types
        usecols = ["Diet_type", "Protein(g)", "Carbs(g)", "Fat(g)"]
        dtypes = {
            "Diet_type": "category",
            "Protein(g)": "float32",
            "Carbs(g)": "float32",
            "Fat(g)": "float32"
        }

        df = pd.read_csv(io.BytesIO(blob_data), usecols=usecols, dtype=dtypes)

        # Create a numeric category code (for efficiency)
        df["Diet_type_code"] = df["Diet_type"].cat.codes

        # Compute mean nutritional values per diet
        avg_macros = (
            df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]]
            .mean()
            .reset_index()
        )

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
