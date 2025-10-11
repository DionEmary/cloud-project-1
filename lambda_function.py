from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os

def process_nutritional_data_from_azurite():
    # Local Azurite connection string
    connect_str = (
        "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;AccountName=devstoreaccount1;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;"
    )

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    container_name = "datasets"
    blob_name = "All_Diets.csv"

    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    blob_data = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(blob_data))

    avg_macros = (
        df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]]
        .mean()
        .reset_index()
    )

    os.makedirs("simulated_nosql", exist_ok=True)

    result = avg_macros.to_dict(orient="records")
    with open("simulated_nosql/results.json", "w") as f:
        json.dump(result, f, indent=4)

    print("Data processed and stored in simulated_nosql/results.json")

if __name__ == "__main__":
    process_nutritional_data_from_azurite()