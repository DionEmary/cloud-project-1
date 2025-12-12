import matplotlib
matplotlib.use("Agg")  # <- must come before importing pyplot
import matplotlib.pyplot as plt
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.cache_helper import get_cached_results

def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    try:
        # Environment variable for connection string
        connect_str = os.environ.get("AzureStorageConnection")
        if not connect_str:
            raise ValueError("AzureStorageConnection environment variable not set")

        container_name = "datasets"

        # PHASE 3: Try to get data from cache first
        cache = get_cached_results(connect_str, container_name)

        if cache and "line_chart" in cache:
            # Use cached data (FAST!)
            avg_macros = pd.DataFrame.from_dict(cache["line_chart"]["data"], orient="index").reset_index()
            avg_macros.columns = ["Diet_type", "Protein(g)", "Carbs(g)", "Fat(g)"]
        else:
            # Fallback: Calculate from original CSV if cache not available
            blob_name = "All_Diets.csv"
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_data = blob_client.download_blob().readall()
            df = pd.read_csv(io.BytesIO(blob_data))
            avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().reset_index()

        # Plot
        plt.figure(figsize=(10, 6))
        for col in ["Protein(g)", "Carbs(g)", "Fat(g)"]:
            plt.plot(avg_macros["Diet_type"], avg_macros[col], marker="o", label=col.replace("(g)", ""))
        plt.title("Average Macronutrients by Diet Type")
        plt.xlabel("Diet Type")
        plt.ylabel("Grams")
        plt.legend()
        plt.tight_layout()

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        plt.close()
        buf.seek(0)

        elapsed = round(time.time() - start_time, 3)

        # Return HTTP response with image
        return func.HttpResponse(
            buf.getvalue(),
            mimetype="image/png",
            headers={"X-Elapsed-Seconds": str(elapsed)}
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
