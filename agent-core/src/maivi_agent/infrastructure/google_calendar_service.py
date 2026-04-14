"""
Servicio de notificaciones con Google Calendar.
Permite agendar recordatorios de pago un día antes y el día del vencimiento.
"""
from shared.init_logger import init_logger
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import random
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from shared.config import settings


class GoogleCalendarNotificationService:
    """Servicio para programar notificaciones de pago usando Google Calendar."""

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(self):
        self.calendar_id = settings.GOOGLE_CALENDAR_ID
        self.credentials_path = settings.GOOGLE_CALENDAR_CREDENTIALS_PATH
        self.logger = init_logger(self.__class__.__name__)
        self.service = None
        
        if not self.credentials_path or self.credentials_path == "":
            self.logger.warning("GOOGLE_CALENDAR_CREDENTIALS_PATH no configurado - notificaciones deshabilitadas")
            return
        
        if not self.calendar_id or self.calendar_id == "":
            self.logger.warning("GOOGLE_CALENDAR_ID no configurado - notificaciones deshabilitadas")
            return
        
        # Inicializar el servicio de Google Calendar
        self._initialize_service()


    def _initialize_service(self):
        """Inicializa el servicio de Google Calendar con las credenciales."""
        try:
            credentials_file = Path(self.credentials_path)
            if not credentials_file.exists():
                self.logger.error(f"Archivo de credenciales no encontrado: {self.credentials_path}")
                return
            
            credentials = service_account.Credentials.from_service_account_file(
                str(credentials_file),
                scopes=self.SCOPES
            )
            
            self.service = build('calendar', 'v3', credentials=credentials)
            self.logger.info("✅ Servicio de Google Calendar inicializado correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error al inicializar Google Calendar: {e}")
            self.service = None


    def _parse_date(self, date_str: str) -> datetime:
        """Convierte fecha dd/MM/yyyy a datetime."""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%d/%M/%Y")
            except ValueError as e:
                raise ValueError(f"Formato de fecha inválido: {date_str}. Use dd/MM/yyyy") from e


    def _create_event_payload(
        self,
        date_time: datetime,
        title: str,
        description: str,
        attendee_emails: Optional[List[str]] = None,
        offset_minutes: int = 0
    ) -> Dict:
        """Crea el payload para crear un evento en Google Calendar."""
        # Calcular hora de inicio con offset
        start_time = date_time.replace(hour=9, minute=0, second=0, microsecond=0)
        start_time = start_time + timedelta(minutes=offset_minutes)
        
        # Google Calendar usa formato RFC3339 para Lima/Peru timezone
        start_iso = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        end_time = start_time + timedelta(hours=1)  # Duración de 1 hora
        end_iso = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        self.logger.info(f"Fecha y hora de inicio: {start_iso} (Lima/Peru)")
        
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_iso,
                'timeZone': 'America/Lima',
            },
            'end': {
                'dateTime': end_iso,
                'timeZone': 'America/Lima',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 60},  # Email 1 hora antes
                    {'method': 'popup', 'minutes': 30},  # Popup 30 minutos antes
                    {'method': 'popup', 'minutes': 0},   # Popup al momento
                ],
            },
            'colorId': '11',  # Rojo para recordatorios de pago
        }
        
        # Agregar asistentes si se proporcionan
        if attendee_emails:
            event['attendees'] = [{'email': email} for email in attendee_emails]
            event['guestsCanModify'] = False
            event['guestsCanInviteOthers'] = False
            event['sendUpdates'] = 'all'  # Enviar notificaciones a todos
        
        return event


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
            Lista con las respuestas de Google Calendar
        """
        # Validar configuración
        if not self.service:
            self.logger.warning("Google Calendar no configurado - saltando notificaciones")
            return []
        
        try:
            due_date = self._parse_date(date_expired)
        except ValueError as e:
            self.logger.error(f"Error al parsear fecha: {e}")
            return []
        
        # Preparar descripción
        description = f"""🔔 Recordatorio de Pago
        Servicio: {service_type}
        Compañía: {company}
        Monto: S/ {amount_total}
        Vencimiento: {date_expired}
        Período: {consumption_period}
        Destinatario: {attendee_name}"""
        
        if phone_number:
            description += f"\nTeléfono: {phone_number}"
        
        # Preparar lista de asistentes
        all_attendees = [attendee_email]
        if additional_emails:
            all_attendees.extend(additional_emails)
        
        results = []
        
        # Notificación 1: Un día antes - Horario aleatorio entre 8:00-9:30 AM
        try:
            day_before = due_date - timedelta(days=1)
            title_before = f"⏰ Mañana vence: {service_type} - S/ {amount_total}"
            
            # Usar minutos aleatorios para evitar conflictos (entre 0 y 90 minutos = 8:00-9:30 AM)
            random_offset = random.randint(0, 90)
            
            event_before = await self._create_event(
                day_before,
                title_before,
                description,
                all_attendees,
                offset_minutes=-60 + random_offset  # Entre 8:00-9:30 AM
            )
            
            if event_before:
                results.append({"type": "day_before", "event": event_before})
                hour = 8 + (random_offset // 60)
                minute = random_offset % 60
                self.logger.info(f"✅ Notificación programada para {day_before.date()} {hour:02d}:{minute:02d} AM")
        except Exception as e:
            self.logger.error(f"❌ Error al programar notificación día anterior: {e}")
        
        # Notificación 2: El mismo día - Horario aleatorio entre 7:00-8:30 AM
        try:
            title_same_day = f"🚨 HOY VENCE: {service_type} - S/ {amount_total}"
            
            # Usar minutos aleatorios diferentes (entre 0 y 90 minutos = 7:00-8:30 AM)
            random_offset_2 = random.randint(0, 90)
            
            event_same_day = await self._create_event(
                due_date,
                title_same_day,
                description,
                all_attendees,
                offset_minutes=-120 + random_offset_2  # Entre 7:00-8:30 AM
            )
            
            if event_same_day:
                results.append({"type": "due_date", "event": event_same_day})
                hour = 7 + (random_offset_2 // 60)
                minute = random_offset_2 % 60
                self.logger.info(f"✅ Notificación programada para {due_date.date()} {hour:02d}:{minute:02d} AM")
        except Exception as e:
            self.logger.error(f"❌ Error al programar notificación mismo día: {e}")
        
        return results


    async def _create_event(
        self,
        date_time: datetime,
        title: str,
        description: str,
        attendee_emails: Optional[List[str]] = None,
        offset_minutes: int = 0
    ) -> Optional[Dict]:
        """Crea un evento en Google Calendar."""
        if not self.service:
            self.logger.error("Servicio de Google Calendar no inicializado")
            return None
        
        event_payload = self._create_event_payload(
            date_time,
            title,
            description,
            attendee_emails,
            offset_minutes
        )
        
        # Log para debug
        self.logger.info(f"Creando evento: {event_payload.get('start', {}).get('dateTime')} - {title}")
        
        try:
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_payload,
                sendUpdates='all' if attendee_emails else 'none'
            ).execute()
            
            self.logger.info(f"✅ Evento creado: {event.get('id')} - {event.get('htmlLink')}")
            return event
            
        except HttpError as error:
            self.logger.error(f"❌ Error HTTP al crear evento: {error}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Excepción al crear evento: {e}")
            return None


    async def delete_event(self, event_id: str) -> bool:
        """
        Elimina un evento del calendario.
        
        Args:
            event_id: ID del evento a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        if not self.service:
            self.logger.error("Servicio de Google Calendar no inicializado")
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            self.logger.info(f"✅ Evento eliminado: {event_id}")
            return True
            
        except HttpError as error:
            self.logger.error(f"❌ Error al eliminar evento: {error}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Excepción al eliminar evento: {e}")
            return False


    async def list_upcoming_events(self, max_results: int = 10) -> List[Dict]:
        """
        Lista los próximos eventos del calendario.
        
        Args:
            max_results: Número máximo de eventos a retornar
            
        Returns:
            Lista de eventos
        """
        if not self.service:
            self.logger.error("Servicio de Google Calendar no inicializado")
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indica UTC
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                self.logger.info('No hay próximos eventos.')
                return []
            
            self.logger.info(f"✅ Se encontraron {len(events)} eventos próximos")
            return events
            
        except HttpError as error:
            self.logger.error(f"❌ Error al listar eventos: {error}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Excepción al listar eventos: {e}")
            return []


# Instancia singleton
_google_calendar_service = None


def get_google_calendar_service() -> GoogleCalendarNotificationService:
    """Obtiene la instancia del servicio de Google Calendar."""
    global _google_calendar_service
    if _google_calendar_service is None:
        _google_calendar_service = GoogleCalendarNotificationService()
    return _google_calendar_service
