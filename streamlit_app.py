import streamlit as st
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import pytesseract
import easyocr

language_options_list = ['aze']  # Add other language options if needed

def init_tesseract():
    tess_version = None
    if not pytesseract.pytesseract.tesseract_cmd:
        st.error("Tesseract binary path not set. Please set the path.")
        st.stop()
    tess_version = pytesseract.get_tesseract_version()[0]
    return tess_version

def pdf_to_text(pdf_file, lang='aze'):
    images = convert_from_path(pdf_file.name)
    extracted_text = ""

    for img in images:
        text = pytesseract.image_to_string(img, lang=lang)
        extracted_text += text + "\n"
    
    return extracted_text

def read_text_from_image(image_file, language='aze'):
    reader = easyocr.Reader([language])
    result = reader.readtext(image_file)
    text = ' '.join([box[1] for box in result])
    return text

# Streamlit config
st.set_page_config(
    page_title="Tesseract OCR",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Init Tesseract
tesseract_version = init_tesseract()

# Streamlit app
st.title("B-Rabbit: OCR for 🇦🇿")

uploaded_file = st.file_uploader(
    "Let's do some magic 🐇",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=False
)
lang = 'aze'  # Fixed language option

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        with st.spinner("Processing PDF..."):
            extracted_text = pdf_to_text(uploaded_file, lang=lang)
    else:
        with st.spinner("Processing image..."):
            extracted_text = read_text_from_image(uploaded_file, language='az')

    # Display the extracted text
    st.subheader("Extracted Text")
    st.text_area("", extracted_text, height=400)
    
    # Option to download the extracted text
    st.download_button(
        label="Download Text",
        data=extracted_text,
        file_name="extracted_text.txt",
        mime="text/plain"
    )
