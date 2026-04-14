"""
WhatsApp Service Implementation
Este módulo proporciona la implementación para enviar mensajes a WhatsApp.
Por ahora usa print, pero está preparado para integrar un proveedor real.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

class WhatsAppService:
    """
    Servicio para enviar mensajes a WhatsApp.
    Implementación provisional con print, lista para integrar un proveedor real.
    """
    
    def __init__(self, url: Optional[str] = None, phone_number_id: Optional[str] = None):
        """
        Inicializa el servicio de WhatsApp.
        
        Args:
            url: URL del proveedor de WhatsApp (ej: Twilio, Meta Business API)
            phone_number_id: ID del número de teléfono desde el cual se enviarán mensajes
        """
        self.url = url
        self.phone_number_id = phone_number_id
        self._initialized = False
        
        if url and phone_number_id:
            self._initialized = True
            print(f"[WhatsApp Service] Inicializado con número: {phone_number_id}")
        else:
            print("[WhatsApp Service] Inicializado en modo simulación (sin credenciales)")
    
    def send_message(
        self, 
        to: str, 
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto a un número de WhatsApp.
        
        Args:
            to: Número de teléfono destino (formato internacional, ej: +34666555444)
            message: Contenido del mensaje a enviar
            message_type: Tipo de mensaje (text, image, document, etc.)
            
        Returns:
            Dict con información del resultado del envío
        """
        timestamp = datetime.now().isoformat()
        
        print("=" * 60)
        print("[WhatsApp Service] ENVIANDO MENSAJE")
        print(f"Timestamp: {timestamp}")
        print(f"Desde: {self.phone_number_id or 'NÚMERO_NO_CONFIGURADO'}")
        print(f"Para: {to}")
        print(f"Tipo: {message_type}")
        print(f"Mensaje:\n{message}")
        print("=" * 60)
        
        # Simular respuesta exitosa
        return {
            "success": True,
            "message_id": f"sim_{timestamp}",
            "timestamp": timestamp,
            "to": to,
            "status": "sent"
        }
    
    def send_template_message(
        self,
        to: str,
        template_name: str,
        template_params: Optional[List[str]] = None,
        language_code: str = "es"
    ) -> Dict[str, Any]:
        """
        Envía un mensaje usando una plantilla predefinida.
        
        Args:
            to: Número de teléfono destino
            template_name: Nombre de la plantilla a usar
            template_params: Parámetros para rellenar la plantilla
            language_code: Código de idioma (ej: es, en, pt)
            
        Returns:
            Dict con información del resultado del envío
        """
        timestamp = datetime.now().isoformat()
        params_str = ", ".join(template_params) if template_params else "sin parámetros"
        
        print("=" * 60)
        print("[WhatsApp Service] ENVIANDO MENSAJE DE PLANTILLA")
        print(f"Timestamp: {timestamp}")
        print(f"Desde: {self.phone_number_id or 'NÚMERO_NO_CONFIGURADO'}")
        print(f"Para: {to}")
        print(f"Plantilla: {template_name}")
        print(f"Idioma: {language_code}")
        print(f"Parámetros: {params_str}")
        print("=" * 60)
        
        return {
            "success": True,
            "message_id": f"sim_template_{timestamp}",
            "timestamp": timestamp,
            "to": to,
            "template": template_name,
            "status": "sent"
        }
    
    def send_media_message(
        self,
        to: str,
        media_url: str,
        media_type: str = "image",
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía un mensaje multimedia (imagen, video, documento, audio).
        
        Args:
            to: Número de teléfono destino
            media_url: URL del archivo multimedia
            media_type: Tipo de medio (image, video, document, audio)
            caption: Texto que acompaña al medio
            
        Returns:
            Dict con información del resultado del envío
        """
        timestamp = datetime.now().isoformat()
        
        print("=" * 60)
        print("[WhatsApp Service] ENVIANDO MENSAJE MULTIMEDIA")
        print(f"Timestamp: {timestamp}")
        print(f"Desde: {self.phone_number_id or 'NÚMERO_NO_CONFIGURADO'}")
        print(f"Para: {to}")
        print(f"Tipo de medio: {media_type}")
        print(f"URL: {media_url}")
        if caption:
            print(f"Caption: {caption}")
        print("=" * 60)
        
        return {
            "success": True,
            "message_id": f"sim_media_{timestamp}",
            "timestamp": timestamp,
            "to": to,
            "media_type": media_type,
            "status": "sent"
        }
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Consulta el estado de un mensaje enviado.
        
        Args:
            message_id: ID del mensaje a consultar
            
        Returns:
            Dict con el estado del mensaje
        """
        print(f"[WhatsApp Service] Consultando estado del mensaje: {message_id}")
        
        return {
            "message_id": message_id,
            "status": "delivered",
            "timestamp": datetime.now().isoformat()
        }
    
    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Marca un mensaje como leído.
        
        Args:
            message_id: ID del mensaje a marcar como leído
            
        Returns:
            Dict con confirmación
        """
        print(f"[WhatsApp Service] Marcando mensaje como leído: {message_id}")
        
        return {
            "success": True,
            "message_id": message_id,
            "marked_as_read": True
        }
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Valida el formato de un número de teléfono.
        
        Args:
            phone_number: Número a validar
            
        Returns:
            True si el formato es válido, False en caso contrario
        """
        # Validación básica: debe empezar con + y tener al menos 10 dígitos
        is_valid = phone_number.startswith('+') and len(phone_number.replace('+', '')) >= 10
        
        print(f"[WhatsApp Service] Validando número {phone_number}: {'✓ Válido' if is_valid else '✗ Inválido'}")
        
        return is_valid
