"""
Punto de entrada principal de la aplicación Maivi Agent.
Ejecuta el sistema de clasificación de recibos.
"""
import base64
from datetime import datetime
from IPython.display import Image, display
from maivi_agent.application.graph import get_workflow

from maivi_agent.domain.entities import ReceiptDataSave, Service
from maivi_agent.infrastructure.image_storage_service import get_instance


def insert_data_mongo():
    from maivi_agent.infrastructure.receipts_repository_impl import ReceiptsRepositoryImpl
    repo= ReceiptsRepositoryImpl()
    
    body= ReceiptDataSave(
        phone_number="51987654321",
        service_type=Service.LUZ,
        is_valid=True,
        is_notified=False,
        amount_total=125.50,
        date_expired="25/02/2026",
        consumption_period="Diciembre 2025",
        company="Luz del Sur",
        link_receipt_image="https://ik.imagekit.io/ljpa/maipevi.mp4"
    )
    receipt_id= repo.save_receipt(body)
    print(f"✅ Recibo insertado con ID: {receipt_id}")

async def imagekit_io():
    image_Service= get_instance()

    image_base64= image_Service._image_to_base64("grafo-agente.png")
    await image_Service.upload_image(file_doc=base64.b64decode(image_base64), folder="/AGENT-AI/recibos", file_name="grafo-agente-ai.png", tags="ARQUITECTURA")

def save_graph_image():
    """Guarda la imagen del grafo en un archivo PNG."""
    compiled_graph = get_workflow()
    
    # Generar la imagen PNG
    png_bytes = compiled_graph.get_graph(xray=True).draw_mermaid_png()
    
    # Guardar en archivo
    with open("graph_workflow.png", "wb") as f:
        f.write(png_bytes)
    
    print("✅ Imagen del grafo guardada en: graph_workflow.png")
    
    # Opcional: También mostrar en Jupyter/IPython
    display(Image(png_bytes))



if __name__ == "__main__":
    #asyncio.run(imagekit_io())
    insert_data_mongo()