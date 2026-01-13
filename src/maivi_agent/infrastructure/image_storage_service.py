import base64
from datetime import datetime
from typing import Optional
from maivi_agent.domain.image_storage import ImageStorage
from imagekitio import ImageKit
from shared.config import settings
from shared.init_logger import init_logger

class ImageStorageService(ImageStorage):
    
    def __init__(self):
        self.imagekit = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY
            )
        self.log= init_logger(self.__class__.__name__)
        
    
    def _imagebase64_to_byte(self, image_base64: str) -> str :
        return base64.b64decode(image_base64)
    
    def _image_to_base64(self, image_url: str) -> str:
        base64_string= ""
        with open(image_url, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read()).decode('utf-8')
        return base64_string
    
    async def upload_image(self, file_doc: str, file_name: str, folder: Optional[str]=None, tags:str = None) -> str:
        self.log.info(f"⬆️  Subiendo imagen a ImageKit en folder: {folder} con nombre: {file_name}")
        try:
            name_file = datetime.now().strftime(f"{file_name}%Y%m%d_%H%M%S.png")
            
            file_byte = self._imagebase64_to_byte(file_doc)
            
            response= self.imagekit.files.upload(
                file=file_byte,
                file_name=name_file,
                folder= folder if folder is not None and folder != "" else "/AGENT-AI/recibos",
                tags=tags
            )
            
            return response.url
            
        except Exception as e:
            self.log.error(f"❌ Error subiendo imagen a ImageKit: {e}", exc_info=True)
            raise e
        
_instance = None

def get_instance() -> ImageStorageService:
    global _instance

    if _instance is None:
        _instance = ImageStorageService()
    return _instance