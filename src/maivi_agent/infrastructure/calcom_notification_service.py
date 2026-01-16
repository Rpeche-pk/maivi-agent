"""
Servicio simple de notificaciones con CAL.COM.
Permite agendar recordatorios de pago un día antes y el día del vencimiento.
"""
from shared.init_logger import init_logger
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import httpx
from shared.config import settings

class CalComNotificationService:
    """Servicio para programar notificaciones de pago usando CAL.COM."""
    
    def __init__(self):
        self.api_key = settings.CALCOM_API_KEY
        self.event_type_id = settings.CALCOM_EVENT_TYPE_ID
        self.base_url = "https://api.cal.com/v2"
        self.logger = init_logger(self.__class__.__name__)
        
        if not self.api_key or self.api_key == "":
            self.logger.warning("CALCOM_API_KEY no configurada - notificaciones deshabilitadas")
        
        if self.event_type_id == 0:
            self.logger.warning("CALCOM_EVENT_TYPE_ID no configurado - notificaciones deshabilitadas")
    
    def _parse_date(self, date_str: str) -> datetime:
        """Convierte fecha dd/MM/yyyy a datetime."""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%d/%M/%Y")
            except ValueError as e:
                raise ValueError(f"Formato de fecha inválido: {date_str}. Use dd/MM/yyyy") from e
    
    def _create_booking_payload(
        self,
        date_time: datetime,
        title: str,
        description: str,
        attendee_email: str,
        attendee_name: str = "Usuario",
        additional_emails: Optional[List[str]] = None
    ) -> Dict:
        """Crea el payload para la API de CAL.COM."""
        start_time = date_time.replace(hour=9, minute=0, second=0, microsecond=0)
        start_iso = start_time.isoformat() + "Z"
        
        # Agregar el título al inicio de la descripción
        full_description = f"{title}\n\n{description}"
        
        payload = {
            "start": start_iso,
            "eventTypeId": self.event_type_id,
            "attendee": {
                "name": attendee_name,
                "email": attendee_email,
                "timeZone": "America/Lima",
                "language": "es"
            },
            "metadata": {
                "title": title,  # Guardamos el título en metadata
                "description": full_description
            },
            "bookingFieldsResponses": {
                "notes": full_description  # El título y descripción aparecen en las notas
            }
        }
        
        # Agregar correos adicionales como guests
        if additional_emails:
            payload["guests"] = additional_emails
        
        return payload
    
    async def schedule_payment_notifications(
        self,
        service_type: str,
        company: str,
        amount_total: float,
        date_expired: str,
        consumption_period: str,
        attendee_email: str,
        attendee_name: str = "Usuario",
        phone_number: Optional[str] = None,
        additional_emails: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Programa 2 notificaciones para un recibo:
        - Un día antes del vencimiento
        - El mismo día del vencimiento
        
        Args:
            service_type: Tipo de servicio (AGUA, LUZ, GAS)
            company: Compañía emisora
            amount_total: Monto a pagar
            date_expired: Fecha de vencimiento (dd/MM/yyyy)
            consumption_period: Período de consumo
            attendee_email: Email principal para las notificaciones
            attendee_name: Nombre del destinatario
            phone_number: Número de teléfono (opcional)
            additional_emails: Lista de emails adicionales para recibir notificaciones
            
        Returns:
            Lista con las respuestas de CAL.COM
        """
        # Validar configuración
        if not self.api_key or self.event_type_id == 0:
            self.logger.warning("CAL.COM no configurado - saltando notificaciones")
            return []
        
        try:
            due_date = self._parse_date(date_expired)
        except ValueError as e:
            self.logger.error(f"Error al parsear fecha: {e}")
            return []
        
        # Preparar descripción
        description = f"""
                🔔 Recordatorio de Pago

                Servicio: {service_type}
                Compañía: {company}
                Monto: S/ {amount_total}
                Vencimiento: {date_expired}
                Período: {consumption_period}
        """.strip()
        
        if phone_number:
            description += f"\nTeléfono: {phone_number}"
        
        results = []
        
        # Notificación 1: Un día antes
        try:
            day_before = due_date - timedelta(days=1)
            title_before = f"⏰ Mañana vence: {service_type} - S/ {amount_total}"
            
            booking_before = await self._create_booking(
                day_before, title_before, description, attendee_email, attendee_name, additional_emails
            )
            
            if booking_before:
                results.append({"type": "day_before", "booking": booking_before})
                self.logger.info(f"Notificación programada para {day_before.date()}")
        except Exception as e:
            self.logger.error(f"Error al programar notificación día anterior: {e}")
        
        # Notificación 2: El mismo día
        try:
            title_same_day = f"🚨 HOY VENCE: {service_type} - S/ {amount_total}"
            
            booking_same_day = await self._create_booking(
                due_date, title_same_day, description, attendee_email, attendee_name, additional_emails
            )
            
            if booking_same_day:
                results.append({"type": "due_date", "booking": booking_same_day})
                self.logger.info(f"Notificación programada para {due_date.date()}")
        except Exception as e:
            self.logger.error(f"Error al programar notificación mismo día: {e}")
        
        return results
    
    async def _create_booking(
        self,
        date_time: datetime,
        title: str,
        description: str,
        attendee_email: str,
        attendee_name: str,
        additional_emails: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Crea un booking en CAL.COM."""
        payload = self._create_booking_payload(
            date_time, title, description, attendee_email, attendee_name, additional_emails
        )
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "cal-api-version": "2024-08-13"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/bookings",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    if result.get("status") == "success":
                        self.logger.info(f"Booking creado: {result.get('data', {}).get('uid')}")
                        return result.get("data")
                    else:
                        self.logger.error(f"CAL.COM error: {result}")
                        return None
                else:
                    self.logger.error(f"Error HTTP {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Excepción al crear booking: {e}")
            return None


# Instancia singleton
_calcom_service = None


def get_calcom_service() -> CalComNotificationService:
    """Obtiene la instancia del servicio de CAL.COM."""
    global _calcom_service
    if _calcom_service is None:
        _calcom_service = CalComNotificationService()
    return _calcom_service
