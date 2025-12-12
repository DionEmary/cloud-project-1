"""
Data Cleaning Blob Trigger

Automatically cleans and processes the All_Diets.csv file when uploaded to Azure Blob Storage.
Phase 3 Requirement: Blob trigger for data cleaning and caching.
"""

import azure.functions as func
import pandas as pd
import logging
import io
import os
from azure.storage.blob import BlobServiceClient


def main(myblob: func.InputStream):
    """
    This function triggers when All_Diets.csv is uploaded/modified in blob storage.
    It cleans the data and saves it as All_Diets_cleaned.csv
    """
    logging.info(f"🚀 Blob trigger activated! Processing: {myblob.name}")
    logging.info(f"📊 Blob size: {myblob.length} bytes")

    try:
        # Read the uploaded CSV from blob
        blob_data = myblob.read()
        df = pd.read_csv(io.BytesIO(blob_data))

        logging.info(f"✅ Loaded CSV with {len(df)} rows and {len(df.columns)} columns")

        # ===== DATA CLEANING STEPS =====

        # 1. Standardize Diet_type column (capitalize first letter, strip whitespace)
        df["Diet_type"] = df["Diet_type"].astype(str).str.strip().str.title()

        # 2. Remove duplicate rows
        original_count = len(df)
        df = df.drop_duplicates()
        duplicates_removed = original_count - len(df)
        if duplicates_removed > 0:
            logging.info(f"🧹 Removed {duplicates_removed} duplicate rows")

        # 3. Remove rows with invalid diet types
        valid_diets = ["Paleo", "Vegan", "Keto", "Mediterranean", "Dash"]
        df = df[df["Diet_type"].isin(valid_diets)]

        # 4. Handle missing values in numeric columns
        numeric_columns = ["Protein(g)", "Carbs(g)", "Fat(g)", "Calories"]
        for col in numeric_columns:
            if col in df.columns:
                # Fill missing values with column mean
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col].fillna(df[col].mean(), inplace=True)

        # 5. Remove rows with all NaN values
        df.dropna(how='all', inplace=True)

        logging.info(f"✅ Data cleaned! Final dataset has {len(df)} rows")

        # ===== SAVE CLEANED DATA BACK TO BLOB STORAGE =====

        # Get connection string from environment
        connect_str = os.environ.get("AzureStorageConnection")
        if not connect_str:
            raise ValueError("AzureStorageConnection environment variable not set")

        # Save cleaned CSV to blob storage
        container_name = "datasets"
        cleaned_blob_name = "All_Diets_cleaned.csv"

        # Convert DataFrame to CSV bytes
        output_buf = io.BytesIO()
        df.to_csv(output_buf, index=False)
        output_buf.seek(0)

        # Upload to blob storage
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
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
