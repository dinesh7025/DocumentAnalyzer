import PyPDF2
from io import BytesIO

def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(BytesIO(file.read()))
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()
