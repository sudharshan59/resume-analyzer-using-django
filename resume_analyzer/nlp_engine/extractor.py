import PyPDF2
from docx2python import docx2python
from io import BytesIO

def extract_text_from_file(file):
    name = file.name.lower()
    if name.endswith('.pdf'):
        reader = PyPDF2.PdfReader(BytesIO(file.read()))
        return "".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith('.docx'):
        doc = docx2python(file)
        return doc.text
    elif name.endswith('.txt'):
        return file.read().decode('utf-8')
    else:
        raise ValueError("Unsupported format. Use PDF, DOCX, or TXT.")