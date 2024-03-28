import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image # Python Image Library to read image
import pandas as pd
import numpy as np
import re
import io
#PIL is used for opening manipulating and saving different image file format
def ImagetoText(path):
    input_img=Image.open(path)
#Image into Array
    img_arr=np.array(input_img)
    reader=easyocr.Reader(['en'])
#OCR reader will be configured to recognize and extract text from images containing English language text.
    text=reader.readtext(img_arr, detail=0)#readtext to extract the text from the image
#detail parameter is set to 0 requesting only the plain text output without any additional details such as bounding boxes, confidence scores, or other information
    return text,input_img
def extracted_text(texts):
    extrd_dict={"NAME":[],"DESIGNATION":[],"COMPANY NAME":[],"CONTACT":[],"EMAIL":[],"WEBSITE":[],"ADDRESS":[],"PINCODE":[]}
    extrd_dict["NAME"].append(texts[0])
    extrd_dict["DESIGNATION"].append(texts[1])
    for i in range(2,len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
            extrd_dict["CONTACT"].append(texts[i])
        elif "@" in texts[i] and ".com" in texts[i]:
            extrd_dict['EMAIL'].append(texts[i])
        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            extrd_dict["WEBSITE"].append(texts[i])
        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
            extrd_dict["PINCODE"].append(texts[i])
        elif re.match(r'^[A-Za-z]',texts[i]):
            extrd_dict["COMPANY NAME"].append(texts[i])
        else:
            remove_colon=re.sub(r'[,;]','',texts[i])
            extrd_dict["ADDRESS"].append(remove_colon)
    for key,value in extrd_dict.items():#handling null values
        if len(value)<1:
            value-"NA"
            extrd_dict[key]=[value]
    return extrd_dict
  st.set_page_config(layout= "wide")
st.title("Biz Card Extraction using OCR")
with st.sidebar:
    select=option_menu("Main Menu",["Home","Upload & Modify","Delete"])
if select=="Home":
    pass
elif select=="Upload & Modify":
    img=st.file_uploader("Upload the Image",type=["png","jpg","jpeg"])
    if img is not None:
        st.image(img,width=300)
        text_image,input_img=ImagetoText(img)
        text_dict=extracted_text(text_image)
        if text_dict:
            st.success("Data is Extracted Successfully")
        df=pd.DataFrame(text_dict)
        st.dataframe(df)
elif select=="Delete":
    pass
