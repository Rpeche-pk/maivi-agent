"""
Centralized prompt management system for LLM interactions.

This module provides a structured way to manage and access prompts used throughout
the application, with support for templates, versioning, and type safety.
"""
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class PromptCategory(Enum):
    """Categories of prompts for better organization."""
    SYSTEM = "system"
    USER = "user"


@dataclass
class PromptTemplate:
    content: str
    category: PromptCategory
    name: Optional[str] = None
    description: Optional[str] = None


class SystemPrompts:
    """System-level prompts for defining AI behavior and context."""
    
    CLASSIFY_ASSISTANT = PromptTemplate(
        content="""
        Eres {name_agent}, un asistente de clasificación de documentos especializado en recibos de servicios básicos en Perú.
        Tu tarea es ANALIZAR el contenido del documento (imagen y/o texto OCR) y devolver únicamente una de las siguientes etiquetas:

        LUZ
        AGUA
        GAS
        NO_VALIDO (cuando NO sea un recibo válido de las empresas indicadas)
        Instrucciones de clasificación:

        ### Instrucciones de clasificación
        Recibo de LUZ (LUZ):

        Es un recibo de la empresa ElectroDunas.
        Verifica que en la parte superior izquierda del documento aparezca claramente el nombre o logo "ElectroDunas".
        Recibo de AGUA (AGUA):

        Es un recibo de la empresa Emapica.
        Verifica que en la parte superior izquierda del documento aparezca claramente el nombre o logo "emapica" o "EMAPICA".
        Recibo de GAS (GAS):

        Es un recibo de la empresa Contugas.
        Verifica que en la parte superior izquierda del documento aparezca claramente el nombre o logo "contugas" o "Contugas".
        Validación de documento (NO_VALIDO):

        ### Validación del documento
        Si el documento no corresponde a un recibo de ElectroDunas, Emapica o Contugas,
        o si no puedes identificar con alta confianza la empresa ni el tipo de servicio,
        responde solo NO_VALIDO.
        Reglas de salida:

        Devuelve exclusivamente una palabra en MAYÚSCULAS de la lista: LUZ, AGUA, GAS o NO_VALIDO.
        No expliques tu razonamiento ni agregues texto adicional.
        """,
        category=PromptCategory.SYSTEM,
        name="CLASSIFY_ASSISTANT",
        description="Prompt de sistema por defecto para el asistente"
    )


class UserPrompts:
    """User-facing prompts for various tasks."""
    
    BUILD_USER_PROMPT_IMAGE = PromptTemplate(
        content="""
        Analiza cuidadosamente la siguiente imagen.

        Si la imagen corresponde a un recibo de servicio público, clasifícalo estrictamente en una de las siguientes categorías:
        - AGUA
        - LUZ
        - GAS

        Responde únicamente con una de esas palabras en mayúsculas.
        No agregues explicaciones, comentarios ni texto adicional.

        Si la imagen no corresponde a un recibo de servicios públicos, responde exactamente:
        NO_VALIDO
        """,
        category=PromptCategory.USER,
        name="BUILD_USER_PROMPT_IMAGE",
        description="Prompt del usuario para clasificar el recibo que el agente recibe por input"
    )

class PromptManager:
    """
    Central manager for all prompts in the application.
    
    Provides utility methods to access, search, and manage prompts.
    """
    
    @staticmethod
    def get_prompt(category: str, name: str) -> Optional[PromptTemplate]:
        """
        Get a specific prompt by category and name.
        
        Args:
            category: Category class name (e.g., 'SystemPrompts')
            name: Prompt name (e.g., 'DEFAULT_ASSISTANT')
            
        Returns:
            PromptTemplate if found, None otherwise
        """
        category_map = {
            'SystemPrompts': SystemPrompts,
            'UserPrompts': UserPrompts,
        }
        
        category_class = category_map.get(category)
        if category_class:
            return getattr(category_class, name, None)
        return None