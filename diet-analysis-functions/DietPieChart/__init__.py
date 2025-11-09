import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend for serverless
import matplotlib.pyplot as plt
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import time
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    
    # Get diet parameter from query string; default to "Keto"
    diet = (req.params.get("diet") or "Keto").strip().title()

    try:
        # Read connection string from environment variable
        connect_str = os.environ.get("AzureStorageConnection")
        if not connect_str:
            raise ValueError("AzureStorageConnection environment variable not set in local.settings.json")
        
        container_name = "datasets"
        blob_name = "All_Diets.csv"

        # Connect to Azurite blob storage
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob().readall()

        # Load CSV into DataFrame
        df = pd.read_csv(io.BytesIO(blob_data))

        # Normalize diet names
        df["Diet_type"] = df["Diet_type"].astype(str).str.strip().str.title()

        # Filter for requested diet
        subset = df[df["Diet_type"] == diet]
        if subset.empty:
            return func.HttpResponse(f"Diet '{diet}' not found in dataset.", status_code=404)

        # Compute average macronutrients
        avg_macros = subset[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()

        # Plot pie chart
        plt.figure(figsize=(6, 6))
        plt.pie(avg_macros, labels=["Protein", "Carbs", "Fat"], autopct="%1.1f%%")
        plt.title(f"Macronutrient Composition for {diet} Diet")
        plt.tight_layout()

        # Save plot to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        plt.close()
        buf.seek(0)

        # Measure execution time
        elapsed = round(time.time() - start_time, 3)

        # Return image as HTTP response with headers
        return func.HttpResponse(
            buf.getvalue(),
            mimetype="image/png",
            headers={
                "X-Elapsed-Seconds": str(elapsed),
                "X-Diet": diet
            }
        )

    except Exception as e:
        return func.HttpResponse(f"Error generating pie chart: {str(e)}", status_code=500)
