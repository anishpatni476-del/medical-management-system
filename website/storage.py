from django.core.files.storage import Storage
from django.conf import settings
from imagekitio import ImageKit


class ImageKitStorage(Storage):

    def __init__(self):
        self.imagekit = ImageKit(
            private_key=settings.IMAGEKIT_PRIVATE_KEY
        )

    def _save(self, name, content):
        file_content = content.read()

        response = self.imagekit.files.upload(
            file=file_content,
            file_name=name,
            folder="/medical-management"
        )

        return response.file_path.strip("/")

    def exists(self, name):
        return False

    def url(self, name):
        return f"{settings.IMAGEKIT_URL_ENDPOINT}/{name}"