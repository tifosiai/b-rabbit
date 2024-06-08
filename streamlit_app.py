import streamlit as st

import helpers.constants as constants
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


def init_sidebar_values():
    '''Initialize all sidebar values of buttons/sliders to default values.
    '''
    if "psm" not in st.session_state:
        st.session_state.psm = tesseract.psm[3]
    if "timeout" not in st.session_state:
        st.session_state.timeout = 20
    if "cGrayscale" not in st.session_state:
        st.session_state.cGrayscale = True
    if "cDenoising" not in st.session_state:
        st.session_state.cDenoising = False
    if "cDenoisingStrength" not in st.session_state:
        st.session_state.cDenoisingStrength = 10
    if "cThresholding" not in st.session_state:
        st.session_state.cThresholding = False
    if "cThresholdLevel" not in st.session_state:
        st.session_state.cThresholdLevel = 128
    if "cRotate90" not in st.session_state:
        st.session_state.cRotate90 = False
    if "angle90" not in st.session_state:
        st.session_state.angle90 = 0
    if "cRotateFree" not in st.session_state:
        st.session_state.cRotateFree = False
    if "angle" not in st.session_state:
        st.session_state.angle = 0


def reset_sidebar_values():
    '''Reset all sidebar values of buttons/sliders to default values.
    '''
    st.session_state.psm = tesseract.psm[3]
    st.session_state.timeout = 20
    st.session_state.cGrayscale = True
    st.session_state.cDenoising = False
    st.session_state.cDenoisingStrength = 10
    st.session_state.cThresholding = False
    st.session_state.cThresholdLevel = 128
    st.session_state.cRotate90 = False
    st.session_state.angle90 = 0
    st.session_state.cRotateFree = False
    st.session_state.angle = 0


def init_session_state_variables():
    '''Initialize all session state values.
    '''
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "raw_image" not in st.session_state:
        st.session_state.raw_image = None
    if "image" not in st.session_state:
        st.session_state.image = None
    if "preview_processed_image" not in st.session_state:
        st.session_state.preview_processed_image = False
    if "crop_image" not in st.session_state:
        st.session_state.crop_image = False
    if "text" not in st.session_state:
        st.session_state.text = None


# streamlit config
st.set_page_config(
    page_title="Tesseract OCR",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# init tesseract
tesseract_version = init_tesseract()
init_sidebar_values()
init_session_state_variables()

# apply custom css
with open(file="helpers/style.css", mode='r', encoding='utf-8') as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

st.title(f"Tesseract OCR :mag_right: {constants.flag_string}")
st.markdown("---")

with st.sidebar:
    st.success(f"Tesseract V **{tesseract_version}** installed")
    st.header("Tesseract OCR Settings")
    st.button('Reset OCR parameters to default', on_click=reset_sidebar_values)
    # FIXME: OEM option does not work in tesseract 4.1.1
    # oem = st.selectbox(label="OCR Engine mode (not working)", options=constants.oem, index=3, disabled=True)
    psm = st.selectbox(label="Page segmentation mode", options=tesseract.psm, key="psm")
    timeout = st.slider(label="Tesseract OCR timeout [sec]", min_value=1, max_value=60, value=20, step=1, key="timeout")
    st.markdown("---")
    st.header("Image Preprocessing")
    st.write("Check the boxes below to apply preprocessing to the image.")
    cGrayscale = st.checkbox(label="Grayscale", value=True, key="cGrayscale")
    cDenoising = st.checkbox(label="Denoising", value=False, key="cDenoising")
    cDenoisingStrength = st.slider(label="Denoising Strength", min_value=1, max_value=40, value=10, step=1, key="cDenoisingStrength")
    cThresholding = st.checkbox(label="Thresholding", value=False, key="cThresholding")
    cThresholdLevel = st.slider(label="Threshold Level", min_value=0, max_value=255, value=128, step=1, key="cThresholdLevel")
    cRotate90 = st.checkbox(label="Rotate in 90° steps", value=False, key="cRotate90")
    angle90 = st.slider("Rotate rectangular [Degree]", min_value=0, max_value=270, value=0, step=90, key="angle90")
    cRotateFree = st.checkbox(label="Rotate in free degrees", value=False, key="cRotateFree")
    angle = st.slider("Rotate freely [Degree]", min_value=-180, max_value=180, value=0, step=1, key="angle")
    st.markdown(
        """---
# About
Streamlit app to extract text from images using Tesseract OCR
## GitHub
<https://github.com/Franky1/Streamlit-Tesseract>
""",
        unsafe_allow_html=True,
    )

# get index of selected oem parameter
# FIXME: OEM option does not work in tesseract 4.1.1
# oem_index = tesseract.oem.index(oem)
oem_index = 3
# get index of selected psm parameter
psm_index = tesseract.psm.index(psm)
# create custom oem and psm config string
custom_oem_psm_config = tesseract.get_tesseract_config(oem_index=oem_index, psm_index=psm_index)

# check if installed languages are available
installed_languages, error = tesseract.get_tesseract_languages()
if error:
    st.error(error)
    st.stop()


col_upload_1, col_upload_2 = st.columns(spec=2, gap="small")


with col_upload_2:
    st.subheader("Select Language :globe_with_meridians:")
    language = st.selectbox(
        label="Select Language",
        options=language_options_list,
        index=constants.default_language_index,
    )
    language_short = list(constants.languages_sorted.keys())[list(constants.languages_sorted.values()).index(language)]
    if language_short not in installed_languages:
        st.error(f'Selected language "{language}" is not installed. Please install language data.')
        st.stop()
    if st.session_state.uploaded_file is not None:
        if st.session_state.image is not None:
            st.markdown("---")
            st.subheader("Run OCR on preprocessed image :mag_right:")
            if st.button("Extract Text"):
                with st.spinner("Extracting Text..."):
                    st.session_state.text, error = tesseract.image_to_string(
                        image=st.session_state.image,
                        language_short=language_short,
                        config=custom_oem_psm_config,
                        timeout=timeout,
                    )
                    if error:
                        st.error(error)