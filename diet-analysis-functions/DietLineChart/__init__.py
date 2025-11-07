import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd, matplotlib.pyplot as plt, io, time

def main(req: func.HttpRequest) -> func.HttpResponse:
    start = time.time()
    try:
        connect_str = (
            "AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/"
            "K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;"
            "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
        )
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_container_client("datasets").get_blob_client("All_Diets.csv")
        blob_data = blob_client.download_blob().readall()

        df = pd.read_csv(io.BytesIO(blob_data))
        avg_macros = df.groupby("Diet_type")[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean().reset_index()

        plt.figure(figsize=(10, 6))
        for col in ["Protein(g)", "Carbs(g)", "Fat(g)"]:
            plt.plot(avg_macros["Diet_type"], avg_macros[col], marker="o", label=col.replace("(g)", ""))
        plt.title("Average Macronutrients by Diet Type")
        plt.xlabel("Diet Type")
        plt.ylabel("Grams")
        plt.legend()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        plt.close()
        buf.seek(0)

        elapsed = round(time.time() - start, 3)
        return func.HttpResponse(buf.getvalue(), mimetype="image/png",
                                 headers={"X-Elapsed-Seconds": str(elapsed)})

    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
