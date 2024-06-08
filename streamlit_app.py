import streamlit as st
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import numpy as np
import cv2
import helpers.constants as constants
import helpers.opencv as opencv
import helpers.pdfimage as pdfimage
import helpers.tesseract as tesseract

language_options_list = list(constants.languages_sorted.values())


def init_tesseract():
    tess_version = None
    # set tesseract binary path
    tesseract.set_tesseract_binary()
    if not tesseract.find_tesseract_binary():
        st.error("Tesseract binary not found in PATH. Please install Tesseract.")
        st.stop()
    # check if tesseract is installed
    tess_version, error = tesseract.get_tesseract_version()
    if error:
        st.error(error)
        st.stop()
    elif not tess_version:
        st.error("Tesseract is not installed. Please install Tesseract.")
        st.stop()
    return tess_version

def pdf_to_text(pdf_path, lang='aze'):
    """
    Convert a PDF file to text using Tesseract OCR.
    
    Parameters:
    pdf_path (str): Path to the PDF file.
    lang (str): Language code for Tesseract OCR (default is 'aze' for Azerbaijani).
    
    Returns:
    str: Extracted text from the PDF.
    """
    images = convert_from_path(pdf_path)
    extracted_text = ""

    for img in images:
        text = pytesseract.image_to_string(img, lang=lang)
        extracted_text += text + "\n"
    
    return extracted_text

def image_to_text(image, lang='aze'):
    """
    Convert an image file to text using Tesseract OCR.
    
    Parameters:
    image (PIL.Image): Image file.
    lang (str): Language code for Tesseract OCR (default is 'aze' for Azerbaijani).
    
    Returns:
    str: Extracted text from the image.
    """
    return pytesseract.image_to_string(image, lang=lang)

# streamlit config
st.set_page_config(
    page_title="Tesseract OCR",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# init tesseract
tesseract_version = init_tesseract()

# Streamlit app
st.title("B-Rabbit: OCR for 🇦🇿")

uploaded_file = st.file_uploader(
    "Let's do some magic 🐇",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=False
)
lang = 'aze'  # Fixed language option
oem_index = 3
# get index of selected psm parameter
psm_index = tesseract.psm.index(psm)
# create custom oem and psm config string
custom_oem_psm_config = tesseract.get_tesseract_config(oem_index=oem_index, psm_index=psm_index)

if uploaded_file is not None:
    if uploaded_file.size > 200 * 1024 * 1024:  # 200 MB limit
        st.error("File size exceeds 200 MB limit. Please upload a smaller file.")
    else:
        with st.spinner("Processing..."):
            # Process PDF file
            if uploaded_file.type == "application/pdf":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf.write(uploaded_file.getbuffer())
                    temp_pdf_path = temp_pdf.name
                extracted_text = pdf_to_text(temp_pdf_path, lang=lang)
                os.remove(temp_pdf_path)

            # Process image file
            else:
                image = Image.open(uploaded_file)
                extracted_text = image_to_text(image, lang=lang)
            
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
