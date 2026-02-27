def extract_text_from_file(file_bytes, filename, content_type):
    import io
    import pdfplumber
    from PIL import Image
    import pytesseract

    text = ""

    if content_type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif content_type in ["image/png", "image/jpeg"]:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)

    elif content_type == "text/plain":
        text = file_bytes.decode("utf-8")

    else:
        raise ValueError(f"Unsupported file format: {content_type}")

    return text