import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import os
import time
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()

    # Get query parameters
    diet = (req.params.get("diet") or "").strip().title()  # e.g., "Keto" or "All"
    keyword = (req.params.get("keyword") or "").strip()  # NEW: Keyword search
    page = int(req.params.get("page") or 1)  # NEW: Page number (default: 1)
    page_size = int(req.params.get("page_size") or 20)  # NEW: Results per page (default: 20)

    valid_diets = ["Paleo", "Vegan", "Keto", "Mediterranean", "Dash"]

    try:
        # Connect to Azurite / Azure Storage
        connect_str = os.environ.get("AzureStorageConnection")
        if not connect_str:
            raise ValueError("AzureStorageConnection not set in local.settings.json")

        container_name = "datasets"
        # UPDATED: Read from cleaned CSV (processed by blob trigger)
        blob_name = "All_Diets_cleaned.csv"

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob().readall()

        # Load cleaned dataset (already normalized by DataCleaningBlobTrigger)
        df = pd.read_csv(io.BytesIO(blob_data))

        # STEP 1: Filter by diet type
        if diet and diet != "All":
            if diet not in valid_diets:
                return func.HttpResponse(
                    f"Invalid diet. Must be one of: {', '.join(valid_diets)}",
                    status_code=400
                )
            filtered_df = df[df["Diet_type"] == diet]
        else:
            filtered_df = df

        # STEP 2: NEW - Filter by keyword (search across all columns)
        if keyword:
            # Search keyword in all text columns (Recipe_name, Cuisine_type, etc.)
            mask = filtered_df.astype(str).apply(
                lambda row: row.str.contains(keyword, case=False, na=False).any(),
                axis=1
            )
            filtered_df = filtered_df[mask]

        # Check if results are empty
        if filtered_df.empty:
            return func.HttpResponse(
                json.dumps({
                    "message": "No records found",
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": 0
                }),
                mimetype="application/json",
                status_code=404
            )

        # STEP 3: NEW - Apply pagination
        total_records = len(filtered_df)
        total_pages = (total_records + page_size - 1) // page_size  # Ceiling division

        # Calculate start and end indices for the current page
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        # Slice the dataframe for the current page
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        # Convert data back to CSV
        output_buf = io.StringIO()
        paginated_df.to_csv(output_buf, index=False)
        output_buf.seek(0)

        elapsed = round(time.time() - start_time, 3)

        # Return CSV response with pagination metadata in headers
        return func.HttpResponse(
            output_buf.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={'all_diets.csv' if diet=='All' else 'filtered_diet.csv'}",
                "X-Elapsed-Seconds": str(elapsed),
                "X-Diet": diet if diet else "All",
                "X-Keyword": keyword if keyword else "",
                "X-Total-Records": str(total_records),
                "X-Page": str(page),
                "X-Page-Size": str(page_size),
                "X-Total-Pages": str(total_pages)
            }
        )

    except ValueError as ve:
        return func.HttpResponse(f"Invalid parameter: {str(ve)}", status_code=400)
    except Exception as e:
        return func.HttpResponse(f"Error processing request: {str(e)}", status_code=500)
