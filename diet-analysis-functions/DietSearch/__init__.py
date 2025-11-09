import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import os
import time

def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    diet = (req.params.get("diet") or "").strip().title()  # e.g., "Keto" or "All"

    valid_diets = ["Paleo", "Vegan", "Keto", "Mediterranean", "Dash"]
    
    try:
        # Connect to Azurite / Azure Storage
        connect_str = os.environ.get("AzureStorageConnection")
        if not connect_str:
            raise ValueError("AzureStorageConnection not set in local.settings.json")

        container_name = "datasets"
        blob_name = "All_Diets.csv"

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob().readall()

        # Load and normalize dataset
        df = pd.read_csv(io.BytesIO(blob_data))
        df["Diet_type"] = df["Diet_type"].astype(str).str.strip().str.title()

        # Determine if filtering is needed
        if diet and diet != "All":
            if diet not in valid_diets:
                return func.HttpResponse(
                    f"Invalid diet. Must be one of: {', '.join(valid_diets)}",
                    status_code=400
                )
            filtered_df = df[df["Diet_type"] == diet]
            if filtered_df.empty:
                return func.HttpResponse(f"No records found for diet '{diet}'.", status_code=404)
        else:
            # Return all diets if diet is "All" or not provided
            filtered_df = df

        # Convert data back to CSV
        output_buf = io.StringIO()
        filtered_df.to_csv(output_buf, index=False)
        output_buf.seek(0)

        elapsed = round(time.time() - start_time, 3)

        # Return CSV response
        return func.HttpResponse(
            output_buf.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={'all_diets.csv' if diet=='All' else 'filtered_diet.csv'}",
                "X-Elapsed-Seconds": str(elapsed),
                "X-Diet": diet if diet else "All"
            }
        )

    except Exception as e:
        return func.HttpResponse(f"Error processing request: {str(e)}", status_code=500)
