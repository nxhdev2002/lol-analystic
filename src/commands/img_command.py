"""
Img command - Send image attachment
"""

from .base_command import BaseCommand
from __uploadAttachments import _uploadAttachment


class ImgCommand(BaseCommand):
    """Command to send an image attachment"""
    
    @property
    def name(self) -> str:
        return "img"
    
    @property
    def description(self) -> str:
        return "Gửi hình ảnh"
    
    def execute(self, client, dataFB, args: str = "") -> dict:
        nameAttachment = "NAME PATH IMAGE"  # Change the image path here (only image!)
        uploadAttachment = _uploadAttachment(nameAttachment, dataFB)  # args=("<nameFile>, dataFB)
        
        return {
            "bodySend": 'Your image!',
            "attachmentID": uploadAttachment.get('attachmentID'),
            "typeAttachment": "image"
        }
