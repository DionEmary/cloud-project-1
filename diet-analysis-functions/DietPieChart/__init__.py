import azure.functions as func
from azure.storage.blob import BlobServiceClient
import pandas as pd, matplotlib.pyplot as plt, io, time

def main(req: func.HttpRequest) -> func.HttpResponse:
    start = time.time()
    diet = req.params.get("diet") or "Keto"
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
        subset = df[df["Diet_type"] == diet]
        if subset.empty:
            return func.HttpResponse(f"Diet '{diet}' not found", status_code=404)

        avg = subset[["Protein(g)", "Carbs(g)", "Fat(g)"]].mean()
        plt.figure(figsize=(6, 6))
        plt.pie(avg, labels=["Protein", "Carbs", "Fat"], autopct="%1.1f%%")
        plt.title(f"Macronutrient Composition for {diet} Diet")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        plt.close()
        buf.seek(0)

        elapsed = round(time.time() - start, 3)
        return func.HttpResponse(buf.getvalue(), mimetype="image/png",
                                 headers={"X-Elapsed-Seconds": str(elapsed),
                                          "X-Diet": diet})

    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
