"""
Ejemplo de uso del servicio de notificaciones de CAL.COM.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from maivi_agent.infrastructure.calcom_notification_service import get_calcom_service


async def main():
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
        attendee_email="usuario@ejemplo.com",
        attendee_name="Juan Pérez",
        phone_number="+51987654321",
        additional_emails=["admin@ejemplo.com", "contador@ejemplo.com"]  # Correos adicionales
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
    asyncio.run(main())
