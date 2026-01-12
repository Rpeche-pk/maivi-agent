from abc import ABC, abstractmethod


class ImageStorage(ABC):
    
    @abstractmethod
    async def upload_image(self, image_base64: str, folder: str, file_name: str) -> str:
        pass