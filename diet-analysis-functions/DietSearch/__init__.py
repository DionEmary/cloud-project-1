import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import os
import time
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    diet = (req.params.get("diet") or "").strip().title()  # e.g., "Keto" or "All"

    # PHASE 3: Keyword search parameter
    keyword = (req.params.get("keyword") or "").strip()

    # PHASE 3: Pagination parameters
    page = int(req.params.get("page") or 1)
    page_size = int(req.params.get("page_size") or 20)

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

        # PHASE 3: Apply keyword search across all columns
        if keyword:
            mask = filtered_df.astype(str).apply(
                lambda row: row.str.contains(keyword, case=False, na=False).any(),
                axis=1
            )
            filtered_df = filtered_df[mask]

        # PHASE 3: Apply pagination
        total_records = len(filtered_df)
        total_pages = (total_records + page_size - 1) // page_size  # Ceiling division

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        # Convert to JSON for better frontend consumption
        result = {
            "data": paginated_df.to_dict(orient="records"),
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages
            }
        }

        elapsed = round(time.time() - start_time, 3)

        # Return JSON response
        return func.HttpResponse(
            json.dumps(result, indent=2),
            mimetype="application/json",
            headers={
                "X-Elapsed-Seconds": str(elapsed),
                "X-Diet": diet if diet else "All",
                "X-Keyword": keyword if keyword else "",
                "X-Total-Records": str(total_records),
                "X-Total-Pages": str(total_pages),
                "X-Current-Page": str(page)
            }
        )

    except Exception as e:
        return func.HttpResponse(f"Error processing request: {str(e)}", status_code=500)
