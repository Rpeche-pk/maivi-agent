"""
Punto de entrada principal de la aplicación Maivi Agent.
Ejecuta el sistema de clasificación de recibos.
"""
import asyncio
import base64
from IPython.display import Image, display
from maivi_agent.application.graph import get_workflow

from maivi_agent.infrastructure.image_storage_service import get_instance


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



if __name__ == "__main__":
    asyncio.run(imagekit_io())
