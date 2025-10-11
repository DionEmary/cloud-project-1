from azure.storage.blob import BlobServiceClient
import pandas as pd
import io
import json
import os

def process_nutritional_data_from_azurite():
    # Local Azurite connection string
    connect_str = (
        "AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
    )

    # Connects to my Local Bloc Storage using the Connection String
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Tge container and blob names for download
    container_name = "datasets"
    blob_name = "All_Diets.csv"

    # 
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    blob_data = blob_client.download_blob().readall()
    
    # Improved by having it only copy the needed columns and specifying dtypes, reducing memory usage
    usecols = ["Diet_type", "Protein(g)", "Carbs(g)", "Fat(g)"]
    dtypes = { 
        # This allows Panda to turn the diet_type from a string to a number making it easier to work with      
        "Diet_type": "category",
        "Protein(g)": "float32",
        "Carbs(g)": "float32",
        "Fat(g)": "float32"
    }
    
    df = pd.read_csv(io.BytesIO(blob_data), usecols=usecols, dtype=dtypes)

    avg_macros = (
        df.groupby("Diet_type", observed=True)[["Protein(g)", "Carbs(g)", "Fat(g)"]]
        .mean(numeric_only=True)
        .reset_index()
    )   

    os.makedirs("simulated_nosql", exist_ok=True)

    result = avg_macros.to_dict(orient="records")
    with open("simulated_nosql/results.json", "w") as f:
        json.dump(result, f, indent=4)

    print("Data processed and stored in simulated_nosql/results.json")

if __name__ == "__main__":
    process_nutritional_data_from_azurite()