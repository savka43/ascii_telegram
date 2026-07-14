from io import BytesIO

from PIL import Image, ImageOps


def open_image(data: bytes | BytesIO) -> Image.Image:
    image = Image.open(data)
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")
