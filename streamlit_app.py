import streamlit as st
from PIL import Image
import os
import tempfile
import easyocr
import helpers.constants as constants
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

def read_text_from_image(image_path, language='az'):
    """
    Read text from an image file using EasyOCR.

    Args:
    - image_path (str): Path to the image file.
    - language (str): Language code (e.g., 'en' for English, 'az' for Azerbaijani).

    Returns:
    - text (str): Extracted text from the image.
    """
    # Initialize the EasyOCR reader
    reader = easyocr.Reader([language])

    # Process the image
    result = reader.readtext(image_path)

    # Extract text from the result
    text = ' '.join([box[1] for box in result])

    return text

# Streamlit config
st.set_page_config(
    page_title="Tesseract OCR",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Init Tesseract (if needed for other purposes)
tesseract_version = init_tesseract()

# Streamlit app
st.title("B-Rabbit: OCR for 🇦🇿")

uploaded_file = st.file_uploader(
    "Let's do some magic 🐇",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=False
)
lang = 'aze'  # Fixed language option

if uploaded_file is not None:
    if uploaded_file.size > 200 * 1024 * 1024:  # 200 MB limit
        st.error("File size exceeds 200 MB limit. Please upload a smaller file.")
    else:
        with st.spinner("Processing..."):
            # Process image file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
                temp_image.write(uploaded_file.getbuffer())
                temp_image_path = temp_image.name
            extracted_text = read_text_from_image(temp_image_path, language='az')
            os.remove(temp_image_path)
        
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
