from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
import os
import shutil


def create_image(name='test'):
    img = BytesIO()
    image = Image.new('RGB', (100, 100))
    image.save(img, 'JPEG')
    img.seek(0)

    image = SimpleUploadedFile(f"{name}.jpg", img.read(), content_type="image/jpeg")

    return image


def clear_images(path):
    if os.path.exists(path):
        shutil.rmtree(path)
