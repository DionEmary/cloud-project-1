import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import os
import logging

def main(myblob: func.InputStream):
    """
    Blob Trigger Function - Automatically runs when All_Diets.csv is uploaded/modified

    This function:
    1. Detects when All_Diets.csv changes in blob storage
    2. Cleans the data (normalize, remove duplicates, handle nulls)
    3. Saves cleaned data to All_Diets_cleaned.csv

    Phase 3 Requirement: Data cleaning happens ONCE when file changes
    """

    logging.info(f"Blob trigger activated for: {myblob.name}")
    logging.info(f"Blob size: {myblob.length} bytes")

    try:
        # Read the uploaded blob data
        blob_data = myblob.read()
        logging.info("Successfully read blob data")

        # Load into DataFrame
        df = pd.read_csv(io.BytesIO(blob_data))
        logging.info(f"Loaded {len(df)} rows from CSV")

        # ===== DATA CLEANING STEPS =====

        # 1. Normalize Diet_type (strip whitespace, title case)
        df["Diet_type"] = df["Diet_type"].astype(str).str.strip().str.title()

        # 2. Normalize Recipe_name (strip whitespace)
        if "Recipe_name" in df.columns:
            df["Recipe_name"] = df["Recipe_name"].astype(str).str.strip()

        # 3. Normalize Cuisine_type (strip whitespace, title case)
        if "Cuisine_type" in df.columns:
            df["Cuisine_type"] = df["Cuisine_type"].astype(str).str.strip().str.title()

        # 4. Handle missing values in numeric columns
        numeric_columns = ["Protein(g)", "Carbs(g)", "Fat(g)"]
        for col in numeric_columns:
            if col in df.columns:
                # Convert to numeric, replacing errors with NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill NaN with 0 or drop rows (choose based on requirement)
                df[col] = df[col].fillna(0)

        # 5. Remove duplicate rows
        rows_before = len(df)
        df = df.drop_duplicates()
        rows_after = len(df)
        duplicates_removed = rows_before - rows_after
        logging.info(f"Removed {duplicates_removed} duplicate rows")

        # 6. Remove rows with invalid diet types
        valid_diets = ["Paleo", "Vegan", "Keto", "Mediterranean", "Dash"]
        df = df[df["Diet_type"].isin(valid_diets)]
        logging.info(f"Filtered to valid diets, {len(df)} rows remaining")

        # 7. Sort by Diet_type and Recipe_name for consistency
        df = df.sort_values(by=["Diet_type", "Recipe_name"])

        # ===== SAVE CLEANED DATA =====

        # Connect to blob storage to save cleaned file
        connect_str = os.environ.get("AzureStorageConnection")
        if not connect_str:
            raise ValueError("AzureStorageConnection not set in environment")

        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = "datasets"
        cleaned_blob_name = "All_Diets_cleaned.csv"

        # Convert cleaned DataFrame to CSV
        output_buf = io.StringIO()
        df.to_csv(output_buf, index=False)
        output_buf.seek(0)

        # Upload cleaned CSV to blob storage
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=cleaned_blob_name
        )
        blob_client.upload_blob(output_buf.getvalue(), overwrite=True)

        logging.info(f"✅ Successfully saved cleaned data to {cleaned_blob_name}")
        logging.info(f"✅ Cleaned dataset has {len(df)} rows and {len(df.columns)} columns")

        # ===== PHASE 3: PRE-CALCULATE AND CACHE CHART RESULTS =====
        logging.info("Starting result calculation for caching...")

        cache_results = {}

        # 1. Bar Chart Data: Average Protein by Diet Type
        avg_protein = df.groupby("Diet_type")["Protein(g)"].mean().to_dict()
        cache_results["bar_chart"] = {
            "data": avg_protein,
            "title": "Average Protein by Diet Type"
        }
        logging.info("✅ Cached bar chart data")

        # 2. Line Chart Data: Average Macronutrients by Diet Type
        avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
        cache_results["line_chart"] = {
            "data": avg_macros.to_dict(orient="index"),
            "title": "Average Macronutrients by Diet Type"
        }
        logging.info("✅ Cached line chart data")

        # 3. Pie Chart Data: Macronutrient composition for each diet
        pie_chart_data = {}
        for diet in valid_diets:
            subset = df[df["Diet_type"] == diet]
            if not subset.empty:
                avg_macros_diet = subset[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().to_dict()
                pie_chart_data[diet] = avg_macros_diet
        cache_results["pie_chart"] = pie_chart_data
        logging.info("✅ Cached pie chart data for all diets")

        # 4. Insights Data: Overall statistics
        insights = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().to_dict(orient="records")
        cache_results["insights"] = {
            "diet_insights": insights
        }
        logging.info("✅ Cached insights data")

        # Save cache to blob storage as JSON
        import json
        cache_blob_name = "cached_results.json"
        cache_json = json.dumps(cache_results, indent=2)

        cache_blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=cache_blob_name
        )
        cache_blob_client.upload_blob(cache_json, overwrite=True)

        logging.info(f"✅ Successfully saved cached results to {cache_blob_name}")
        logging.info("🎉 Data cleaning and caching complete!")

    except Exception as e:
        logging.error(f"❌ Error in data cleaning: {str(e)}")
        raise
