"""
Punto de entrada principal de la aplicación Maivi Agent.
Ejecuta el sistema de clasificación de recibos.
"""
import asyncio

from pydantic import BaseModel, Field
from llm.infrastructure import get_container
from llm.domain.llm_entities import LLMRequestConfig, UserInputType
from shared.prompts import PromptManager
import base64


async def classify_receipt_example():
    """Ejemplo de clasificación de recibo usando el contenedor de dependencias."""
    image_path = "./architecture/gas.png"
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    # Obtener el contenedor con todas las dependencias (Singleton)
    container = get_container()
    
    # El orquestador ya tiene todas sus dependencias inyectadas
    orchestrator = container.llm_orchestrator
    
    # structure output
    class ClassifyModel(BaseModel):
        service : str = Field(description= "Servicio de AGUA, LUZ o GAS")
    
    # Configurar la solicitud para clasificación de texto
    request_config = LLMRequestConfig(
        input_type=UserInputType.IMAGE,
        prompt= PromptManager.get_prompt("SystemPrompts","CLASSIFY_ASSISTANT").content.format(name_agent ="maivi"),
        structured_output= ClassifyModel
    )
    
    # Ejecutar el LLM
    chain = await orchestrator.execute_llm(request_config)
    
    # Invocar la cadena con un mensaje de prueba
    result = await chain.ainvoke({
        "text_content": "Clasificame correctamente la siguiente imagen, si se trata de un recibo responde: AGUA, LUZ O GAS",
        "image_base64" : image_base64
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
