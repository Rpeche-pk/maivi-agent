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
    
    PROMPT_EXTRACT_DATA = PromptTemplate( 
        content="""
        Eres {name_agent}, un asistente experto en análisis y extracción de información de recibos de servicios públicos en Perú.
        Tu tarea es analizar cuidadosamente la imagen del recibo proporcionada y extraer la siguiente información de manera precisa:
        
        ## TUS CAPACIDADES:
        1. Análisis preciso de imágenes de recibos de servicios
        2. Identificación de información clave en documentos con diferentes formatos
        3. Extracción estructurada de datos financieros y administrativos
        4. Normalización de fechas y montos a formatos estándar
        5. Identificación confiable de empresas prestadoras de servicios

        ## INFORMACIÓN A EXTRAER:

        1. **MONTO TOTAL A PAGAR (amount_total)**:
        - Busca las etiquetas: "TOTAL A PAGAR", "MONTO TOTAL A PAGAR", "TOTAL A PAGAR S/."
        - Extrae solo el valor numérico (sin símbolos de moneda)
        - Formato: número decimal (ejemplo: 15.00, 218.00, 38.30)
        - Ignora centavos si aparecen asteriscos o están censurados

        2. **FECHA DE VENCIMIENTO (date_expired)**:
        - Busca las etiquetas: "FECHA DE VENCIMIENTO", "Último día de pago", "FECHA VENCIMIENTO"
        - Formato obligatorio: dd/MM/yyyy (ejemplo: 12/09/2016, 15/08/2024)
        - Si encuentras formato diferente, conviértelo al formato requerido

        3. **PERÍODO DE CONSUMO (consumption_period)**:
        - Busca las etiquetas: "Periodo de Facturación", "FACTURACION", "Mes de consumo", "Consumo del Periodo"
        - Identifica el mes y año del período facturado
        - Formato preferido: "Mes Año" (ejemplo: "Octubre 2024", "Setiembre 2016", "Julio 2024")
        - También acepta formatos como "SET 2016", "AGO 2016" pero conviértelos al formato preferido

        4. **COMPAÑÍA (company)**:
        - Identifica la empresa prestadora del servicio entre:
            * **EMAPICA**: Empresa Municipal de Agua Potable de Ica (recibos de agua)
            * **ELECTRODUNAS**: Electro Dunas S.A.A. (recibos de luz/electricidad)
            * **CONTUGAS**: Contugas S.A.C. (recibos de gas natural)
        - Busca el logotipo, encabezado o nombre de la empresa en la parte superior del recibo
        - Devuelve el nombre exacto: "EMAPICA", "ELECTRODUNAS" o "CONTUGAS"

        ## INSTRUCCIONES IMPORTANTES:

        - Lee cuidadosamente TODO el contenido del recibo antes de extraer
        - Los montos pueden estar parcialmente censurados con asteriscos (******), extrae los dígitos visibles
        - Las fechas pueden aparecer en diferentes formatos, normalízalas siempre a dd/MM/yyyy
        - Si algún campo no está claramente visible o no existe, utiliza None para ese campo
        - Para el período de consumo, busca tanto en "Mes de consumo" como en "Facturación"
        - Presta atención especial al tipo de servicio para identificar correctamente la compañía
        - Verifica que el monto total coincida con la sección de pago, no confundas con subtotales

        ## CONTEXTO ADICIONAL:
        - Los recibos pueden contener múltiples fechas (emisión, consumo, vencimiento) - asegúrate de capturar la fecha de vencimiento
        - Los montos pueden incluir IGV e intereses, busca el "TOTAL A PAGAR" final
        - El período de consumo puede estar en formato abreviado (SET = Setiembre, AGO = Agosto, etc.)

        Analiza el recibo y devuelve la información estructurada según el modelo Pydantic proporcionado.
        Siempre mantén un alto estándar de precisión y profesionalismo en tu análisis.""",

        category=PromptCategory.SYSTEM,
        name="PROMPT_EXTRACT_DATA",
        description="Prompt de sistema que permite la extracción de data de los recibos."
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
    
    USER_PROMPT_EXTRACT_DATA = PromptTemplate(
        content="""
        Analiza cuidadosamente el recibo de servicio público en la imagen proporcionada y extrae la siguiente información:

        ## DATOS A EXTRAER:

        ### 1. MONTO TOTAL A PAGAR (amount_total)
        **Buscar en:**
        - "TOTAL A PAGAR"
        - "MONTO TOTAL A PAGAR"
        - "TOTAL A PAGAR S/."
        - "Monto Total a Pagar:"

        **Instrucciones:**
        - Extrae SOLO el valor numérico sin símbolos de moneda (S/., S/, $)
        - Formato: número decimal con punto (ejemplo: 15.00, 218.00, 38.30)
        - Si hay asteriscos censurando parte del monto (ejemplo: ******15.00), extrae los dígitos visibles
        - NO confundas con subtotales, IGV o conceptos individuales
        - Busca el monto final más prominente en el recibo

        ### 2. FECHA DE VENCIMIENTO (date_expired)
        **Buscar en:**
        - "FECHA DE VENCIMIENTO:"
        - "Último día de pago"
        - "FECHA VENCIMIENTO"
        - "Vence:"
        - "Fecha límite de pago"

        **Instrucciones:**
        - Formato OBLIGATORIO de salida: dd/MM/yyyy
        - Ejemplos válidos: "12/09/2016", "15/08/2024", "31/12/2025"
        - Si encuentras formato dd/MM/yy, completa el año (16 → 2016, 24 → 2024)
        - Si encuentras formato con nombre de mes, conviértelo a numérico
        - IMPORTANTE: NO confundas con "Fecha de emisión" o "Fecha de consumo"

        ### 3. PERÍODO DE CONSUMO (consumption_period)
        **Buscar en:**
        - "Periodo de Facturación"
        - "FACTURACION"
        - "Mes de consumo"
        - "Consumo del Periodo"
        - "Período"
        - Encabezado con mes y año

        **Instrucciones:**
        - Formato preferido: "Mes Año" (ejemplo: "Octubre 2024", "Setiembre 2016")
        - Si encuentras abreviaciones, expándelas:
        * SET → Setiembre
        * AGO → Agosto
        * ENE → Enero
        * FEB → Febrero
        * MAR → Marzo
        * ABR → Abril
        * MAY → Mayo
        * JUN → Junio
        * JUL → Julio
        * OCT → Octubre
        * NOV → Noviembre
        * DIC → Diciembre
        - Si hay rango de fechas, identifica el mes/período que representa

        ### 4. COMPAÑÍA (company)
        **Identificar entre:**
        - **EMAPICA**: Agua y alcantarillado (busca logo con gotas, colores azules/celestes, "E.P.S. EMAPICA")
        - **ELECTRODUNAS**: Energía eléctrica (busca logo eléctrico, colores naranja/amarillo, consumo en kWh)
        - **CONTUGAS**: Gas natural (busca logo con llama/gas, colores verdes, consumo en m³, "Grupo Energía Bogotá")

        **Instrucciones:**
        - Revisa el logo y encabezado principal del recibo
        - Verifica que el tipo de servicio coincida con la empresa
        - Devuelve el nombre EXACTO: "EMAPICA", "ELECTRODUNAS" o "CONTUGAS"
        - Si no puedes identificar con certeza, devuelve None

        ## PROCESO DE ANÁLISIS:
        1. **Observa la imagen completa** para tener contexto general
        2. **Identifica la empresa** mediante logo y colores corporativos
        3. **Localiza el monto total** (usualmente destacado en tamaño grande o recuadro)
        4. **Busca la fecha de vencimiento** (distínguelo de otras fechas)
        5. **Identifica el período facturado** (puede estar en varias secciones)
        6. **Valida la consistencia** entre todos los datos extraídos
        """,
        category=PromptCategory.USER,
        name="USER_PROMPT_EXTRACT_DATA",
        description="Prompt ingresado por el usuario para la clasificación de recibo"
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