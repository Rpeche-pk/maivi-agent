"""
Ejemplo simple de uso del servicio de Google Calendar para notificaciones de pago.
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir / "src"))

from maivi_agent.infrastructure.google_calendar_service import get_google_calendar_service


async def test_schedule_notifications():
    """Prueba la programación de notificaciones de pago."""
    
    # Obtener el servicio
    calendar_service = get_google_calendar_service()
    
    # Datos de ejemplo de un recibo
    result = await calendar_service.schedule_payment_notifications(
        service_type="LUZ",
        company="ENEL",
        amount_total=150.75,
        date_expired="20/02/2026",  # 8 días después de hoy (12/02/2026)
        consumption_period="Enero 2026",
        attendee_email="tu_email@gmail.com",  # 👈 Cambia este email
        attendee_name="Juan Pérez",
        phone_number="+51987654321",
        additional_emails=["otro_email@gmail.com"]  # Opcional
    )
    
    print("\n" + "="*60)
    print("RESULTADOS DE LA PROGRAMACIÓN")
    print("="*60)
    
    if result:
        for notification in result:
            print(f"\n📅 Tipo: {notification['type']}")
            event = notification['event']
            print(f"   ID: {event.get('id')}")
            print(f"   Título: {event.get('summary')}")
            print(f"   Inicio: {event.get('start', {}).get('dateTime')}")
            print(f"   Link: {event.get('htmlLink')}")
    else:
        print("\n⚠️  No se programaron notificaciones")
        print("Verifica tu configuración en el archivo .env:")
        print("  - GOOGLE_CALENDAR_ID")
        print("  - GOOGLE_CALENDAR_CREDENTIALS_PATH")
    
    print("\n" + "="*60)


async def test_list_upcoming_events():
    """Lista los próximos eventos del calendario."""
    
    calendar_service = get_google_calendar_service()
    
    print("\n" + "="*60)
    print("PRÓXIMOS EVENTOS")
    print("="*60)
    
    events = await calendar_service.list_upcoming_events(max_results=5)
    
    if events:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"\n📌 {event['summary']}")
            print(f"   Inicio: {start}")
            print(f"   ID: {event['id']}")
    else:
        print("\nNo hay eventos próximos o el servicio no está configurado")
    
    print("\n" + "="*60)


async def main():
    """Función principal."""
    print("\n🔔 Test de Google Calendar Notification Service")
    print("="*60)
    
    # Descomentar la prueba que quieras ejecutar:
    
    # 1. Programar notificaciones de pago
    await test_schedule_notifications()
    
    # 2. Listar próximos eventos
    # await test_list_upcoming_events()


if __name__ == "__main__":
    asyncio.run(main())
