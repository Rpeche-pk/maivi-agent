from typing import Optional
from maivi_agent.domain.image_storage import ImageStorage
import os
from imagekitio import ImageKit
from shared.config import settings
from shared.init_logger import init_logger

class ImageStorageService(ImageStorage):
    
    def __init__(self):
        self.imagekit = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY,
                public_key=settings.IMAGEKIT_PUBLIC_KEY,
                url_endpoint=settings.URL_ENDPOINT_IMAGEKIT
            )
        self.log= init_logger(self.__class__.__name__)
        
    
    async def upload_image(self, image_base64: str, folder: str, file_name: str, options: Optional[dict]=None) -> str:
        self.log.info(f"⬆️  Subiendo imagen a ImageKit en folder: {folder} con nombre: {file_name}")
        try:
            response= self.imagekit.files.upload(
                file=image_base64,
                file_name=file_name,
                folder="/AGENT-AI/recibos",
                options= options if options else {}
            )
            
            print(response)
            
            return f"{self.url_endpoint}{response['response']['filePath']}"
            
        except Exception as e:
            self.log.error(f"❌ Error subiendo imagen a ImageKit: {e}", exc_info=True)
            raise e
        
image_Service= ImageStorageService()

image_Service.upload_image()
