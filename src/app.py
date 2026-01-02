"""
Punto de entrada principal de la aplicación Maivi Agent.
Ejecuta el sistema de clasificación de recibos.
"""
import asyncio

from pydantic import BaseModel, Field
from llm.domain.llm_entities import LLMRequestConfig, UserInputType
from shared.prompts import PromptManager
import base64
from shared.init_logger import init_logger
from enum import Enum
from maivi_agent.infrastructure.container import get_container

log= init_logger("app.py")

class Service(Enum):
    AGUA = "AGUA"
    LUZ = "LUZ"
    GAS = "GAS"
    NO_VALIDO = "NO_VALIDO"

async def classify_receipt_example():
    """Ejemplo de clasificación de recibo usando el contenedor de dependencias."""
    image_path = "./architecture/agua.jpg"
    
    def encode_image_to_base64(image_path: str) -> str:
        """Codifica una imagen a base64 para su uso en la solicitud LLM."""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode("utf-8")
        
    image_base64 = encode_image_to_base64(image_path)
    print("Imagen codificada a base64 para la solicitud LLM. {}".format(image_base64[:30] + "..."))
    # Obtener el contenedor con todas las dependencias (Singleton)
    container = get_container()
    
    # El orquestador ya tiene todas sus dependencias inyectadas
    orchestrator = container.llm_orchestrator
    
    # structure output
    class ClassifyModel(BaseModel):
        service : Service = Field(description= "Servicio de AGUA, LUZ o GAS")
    
    # Configurar la solicitud para clasificación de texto
    request_config = LLMRequestConfig(
        input_type=UserInputType.IMAGE,
        image_base64=image_base64,
        prompt= PromptManager.get_prompt("SystemPrompts","CLASSIFY_ASSISTANT").content.format(name_agent ="maivi"),
        structured_output= ClassifyModel
    )
    
    # Ejecutar el LLM
    chain = await orchestrator.execute_llm(request_config)

    # Invocar la cadena con un mensaje de prueba
    result = await chain.ainvoke({
        "text_content": PromptManager.get_prompt("UserPrompts","BUILD_USER_PROMPT_IMAGE").content
    })
    
    
    print(f"Resultado de clasificación: {result}")


def main():
    """Función principal de la aplicación."""
    print("=" * 60)
    print("MAIVI AGENT - Sistema de Clasificación de Recibos")
    print("=" * 60)
    
    # Ejecutar ejemplo de clasificación
    asyncio.run(classify_receipt_example())
    
    print("=" * 60)
    print("Aplicación finalizada")
    print("=" * 60)


if __name__ == "__main__":
    main()
