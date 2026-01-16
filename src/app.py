"""
Punto de entrada principal de la aplicación Maivi Agent.
Ejecuta el sistema de clasificación de recibos.
"""
import asyncio
import base64
from datetime import datetime
from IPython.display import Image, display
from maivi_agent.application.graph import get_workflow

from maivi_agent.domain.entities import ReceiptDataSave, Service
from maivi_agent.infrastructure.image_storage_service import get_instance

from maivi_agent.infrastructure.calcom_notification_service import get_calcom_service


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
    


async def calcom_notifications():
    """Ejemplo de programación de notificaciones."""
    
    print("=" * 60)
    print("Ejemplo de Servicio de Notificaciones CAL.COM")
    print("=" * 60)
    print()
    
    # Obtener el servicio
    calcom = get_calcom_service()
    
    # Datos de ejemplo de un recibo
    print("📋 Programando notificaciones para un recibo...")
    print("   📧 Email principal: usuario@ejemplo.com")
    print("   📧 Emails adicionales: admin@ejemplo.com, contador@ejemplo.com")
    print()
    
    notifications = await calcom.schedule_payment_notifications(
        service_type="LUZ",
        company="ELECTRODUNAS",
        amount_total=150.50,
        date_expired="25/01/2026",  # dd/MM/yyyy
        consumption_period="Diciembre 2025",
        attendee_email="pecheaparcana1998@gmail.com",
        attendee_name="Luis Peche",
        phone_number="+51966524537",
        additional_emails=["jessepickman20@gmail.com"]  # Correos adicionales
    )
    
    print(f"✅ Resultado: {len(notifications)} notificaciones programadas")
    print()
    
    for notif in notifications:
        notif_type = "Un día antes" if notif["type"] == "day_before" else "Día del vencimiento"
        booking = notif["booking"]
        print(f"  📅 {notif_type}")
        print(f"     ID: {booking.get('id')}")
        print(f"     Inicio: {booking.get('start')}")
        print()


if __name__ == "__main__":
    #asyncio.run(imagekit_io())
    #insert_data_mongo()
    #save_graph_image()
    asyncio.run(calcom_notifications())