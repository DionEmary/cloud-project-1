import os
import time
import io
import pandas as pd
import matplotlib.pyplot as plt
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.cache_helper import get_cached_results

def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()

    try:
        # Read connection info
        conn_str = os.environ["AzureStorageConnection"]
        container_name = "datasets"

        # PHASE 3: Try to get data from cache first
        cache = get_cached_results(conn_str, container_name)

        if cache and "bar_chart" in cache:
            # Use cached data (FAST!)
            avg_protein = pd.Series(cache["bar_chart"]["data"])
        else:
            # Fallback: Calculate from cleaned CSV if cache not available
            blob_name = "All_Diets_cleaned.csv"
            blob_service = BlobServiceClient.from_connection_string(conn_str)
            blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
            blob_data = blob_client.download_blob().readall()
            df = pd.read_csv(io.BytesIO(blob_data))
            avg_protein = df.groupby("Diet_type")["Protein(g)"].mean()
        plt.figure(figsize=(8,5))
        avg_protein.plot(kind="bar", color="steelblue")
        plt.title("Average Protein by Diet Type")
        plt.xlabel("Diet Type")
        plt.ylabel("Protein (g)")
        plt.tight_layout()

        # Convert to bytes
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format="png", dpi=150)
        plt.close()
        img_bytes.seek(0)

        # Compute elapsed time
        elapsed = round(time.time() - start_time, 3)

        # Return with elapsed time in header
        return func.HttpResponse(
            img_bytes.getvalue(),
            mimetype="image/png",
            headers={"X-Elapsed-Seconds": str(elapsed)}
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)
