from abc import ABC, abstractmethod
from typing import Optional


class ImageStorage(ABC):
    
    @abstractmethod
    async def upload_image(self, file_doc: str, file_name: str,folder: Optional[str] = None, tags:str = None) -> str:
        """
        Carga las images a un proveedor de guardado de imagenes
        Args:
            file_doc: Contenido del archivo a subir en base64
            folder: folder donde se ubicará el archivo
            file_name: nombre del archivo
            tags: identificador para el archivo a subir
        Returns:
            str: Url de acceso para el archivo
        """
        pass