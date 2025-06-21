import pytesseract
from PIL import Image
from PIL import UnidentifiedImageError
from io import BytesIO

def extract_text_from_image(file):
    try:
        image = Image.open(BytesIO(file.read()))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except UnidentifiedImageError:
        return "ERROR: Invalid or corrupted image file"
