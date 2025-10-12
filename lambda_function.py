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

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    container_name = "datasets"
    blob_name = "All_Diets.csv"

    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    blob_data = blob_client.download_blob().readall()
    
    # This code below was added as a improvement for Task 5
    # This is used to tell the code, which columns to load so we don't load unneeded data
    usecols = ["Diet_type", "Protein(g)", "Carbs(g)", "Fat(g)"] 
    # Panda has ways we can optomize how it reads and uses the data, the first one tells it we can turn diet_type to numeric values (Vegan = 0, Keto = 1, etc.)
    # The other 3 columns simply tell it to create a smaller number as Panda defaults to float64 which has more decimal places, but we don't need that many for the macros.
    dtypes = {
        # Stores diet_type as a number and string in a map so we can calculate with a numeric value, but display a string.
        "Diet_type": "category",
        # Use float32 to save memory, we don't need the extra precision of float64 for these values
        "Protein(g)": "float32",
        "Carbs(g)": "float32",
        "Fat(g)": "float32"
    }

    # This is just the same pd.read_csv but using the variables established above
    df = pd.read_csv(io.BytesIO(blob_data), usecols=usecols, dtype=dtypes)

    # This line creates a new column that has the numeric values for diet_type, 
    # this way we can use numbers rather than strings to determine which diet the meal is faster than before, 
    # and is the reason we did "Diet_Type": "category" earlier
    df["Diet_type_code"] = df["Diet_type"].cat.codes

    avg_macros = (
        # Even though it says it is using diet_type not Diet_type_code, it is still using the numeric values behind the scenes
        # As since we set that dtype earlier, panda knows it has a numeric value it can use for processing, but this way it still displays the 
        # string value when we print it out or save it to a file.
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