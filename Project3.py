import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import mysql.connector
import base64

def ImagetoText(path):
    input_img = Image.open(path)
    # Image into Array
    img_arr = np.array(input_img)
    reader = easyocr.Reader(['en'])
    # OCR reader will be configured to recognize and extract text from images containing English language text.
    text = reader.readtext(img_arr, detail=0)
    # detail parameter is set to 0 requesting only the plain text output without any additional details such as bounding boxes, confidence scores, or other information
    return text, input_img

def extracted_text(texts):
    extrd_dict = {"NAME": [], "DESIGNATION": [], "COMPANY NAME": [], "CONTACT": [], "EMAIL": [],
                  "WEBSITE": [], "ADDRESS": [], "PINCODE": []}
    extrd_dict["NAME"].append(texts[0])
    extrd_dict["DESIGNATION"].append(texts[1])
    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and '-' in texts[i]):
            extrd_dict["CONTACT"].append(texts[i])
        elif "@" in texts[i] and ".com" in texts[i]:
            extrd_dict['EMAIL'].append(texts[i])
        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            small = texts[i].lower()
            extrd_dict["WEBSITE"].append(small)
        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
            extrd_dict["PINCODE"].append(texts[i])
        elif re.match(r'^[A-Za-z]', texts[i]):
            extrd_dict["COMPANY NAME"].append(texts[i])
        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extrd_dict["ADDRESS"].append(remove_colon)
    for key, value in extrd_dict.items():
        if len(value) > 0:
            concadenate = "".join(value)
            extrd_dict[key] = [concadenate]
        else:
            value = "NA"
            extrd_dict[key] = [value]
    return extrd_dict

def convert_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

st.set_page_config(layout="wide")
st.title("Biz Card Extraction using OCR")

with st.sidebar:
    select = option_menu("Main Menu", ["Home", "Upload & Modify", "Delete"])

if select == "Home":
    pass
elif select == "Upload & Modify":
    img = st.file_uploader("Upload the Image", type=["png", "jpg", "jpeg"])
    if img is not None:
        st.image(img, width=300)
        text_image, input_img = ImagetoText(img)
        text_dict = extracted_text(text_image)
        if text_dict:
            st.success("Data is Extracted Successfully")
        df = pd.DataFrame(text_dict)
        # Convert image to base64 string
        img_base64 = convert_image_to_base64(input_img)
        # Create a dataframe containing the base64-encoded image data
        df_1 = pd.DataFrame({"Image": [img_base64]})
        # Concatenate the dataframes along columns
        concat_df = pd.concat([df, df_1], axis=1)
        st.dataframe(concat_df)
        button_1 = st.button("Save")
        if button_1:
            # Storing the dataframe in Database
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password=""
            )
            mycursor = mydb.cursor(buffered=True)
            mycursor.execute("USE BIZ")
            mycursor.execute('''CREATE TABLE IF NOT EXISTS BIZ
                                (name varchar(225),
                                 designation varchar(225),
                                 company_name varchar(225),
                                 contact varchar(225),
                                 email varchar(225),
                                 website text,
                                 address text,
                                 pincode varchar(225),
                                 image text)''')
            mydb.commit()
            insert_query = '''INSERT INTO BIZ (name, designation, company_name, contact, email, website, address, pincode, image)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
            datas = concat_df.values.tolist()[0]
            mycursor.execute(insert_query, datas)
            mydb.commit()
            st.success("Saved Successfully")
    method = st.radio("Select the method", ("Preview", "Modify"))
    if method == "Preview":
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("USE BIZ")
        select_query = "SELECT * FROM BIZ"
        mycursor.execute(select_query)
        table = mycursor.fetchall()
        mydb.commit()
        table_df = pd.DataFrame(table, columns=("name", "designation", "company_name", "contact", "email", "website", "address", "pincode", "image"))
        st.dataframe(table_df)
    elif method=="Modify":
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("USE BIZ")
        select_query = "SELECT * FROM BIZ"
        mycursor.execute(select_query)
        table = mycursor.fetchall()
        mydb.commit()
        table_df = pd.DataFrame(table, columns=("name", "designation", "company_name", "contact", "email", "website", "address", "pincode", "image"))
        col1,col2=st.columns(2)
        with col1:
            selected_name=st.selectbox("Select the name",table_df["name"])
        df_3=table_df[table_df["name"]==selected_name]
        st.dataframe(df_3)
        df_4=df_3.copy()
        col1,col2=st.columns(2)
        with col1:
            mo_name=st.text_input("name",df_3["name"].unique()[0])
            mo_desi=st.text_input("designation",df_3["designation"].unique()[0])
            mo_com_name=st.text_input("company_name",df_3["company_name"].unique()[0])
            mo_contact=st.text_input("contact",df_3["contact"].unique()[0])
            mo_email=st.text_input("email",df_3["email"].unique()[0])
            df_4["name"]=mo_name
            df_4["designation"]=mo_desi
            df_4["company_name"]=mo_com_name
            df_4["contact"]=mo_contact
            df_4["email"]=mo_email
        with col2:
            mo_website=st.text_input("website",df_3["website"].unique()[0])
            mo_address=st.text_input("address",df_3["address"].unique()[0])
            mo_pincode=st.text_input("pincode",df_3["pincode"].unique()[0])
            mo_image=st.text_input("image",df_3["image"].unique()[0])
            df_4["website"]=mo_website
            df_4["address"]=mo_address
            df_4["pincode"]=mo_pincode
            df_4["image"]=mo_image

        st.dataframe(df_4)
        col1,col2=st.columns(2)
        with col1:
            button_3=st.button("Modify")
        if button_3:
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("USE BIZ")
        mycursor.execute(f"Delete from BIZ where name='{selected_name}'")
        mydb.commit()
        #Insert Query
        insert_query = '''INSERT INTO BIZ (name, designation, company_name, contact, email, website, address, pincode, image)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        datas = df_4.values.tolist()[0]
        mycursor.execute(insert_query, datas)
        mydb.commit()
        st.success("Modified Successfully")

elif select == "Delete":
    mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="")
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("USE BIZ")
    col1,col2=st.columns(2)
    with col1:
        select_query = "SELECT name FROM BIZ"
        mycursor.execute(select_query)
        table1 = mycursor.fetchall()
        mydb.commit()
        names=[]
        for i in table1:
            names.append(i[0])
        name_select=st.selectbox("Select the name",names)
    with col2:
        select_query = f"SELECT designation FROM BIZ where name='{name_select}'"
        mycursor.execute(select_query)
        table2 = mycursor.fetchall()
        mydb.commit()
        designations=[]
        for j in table2:
            designations.append(j[0])
        designation_select=st.selectbox("Select the designation",designations)
    if name_select and designation_select:
        remove=st.button("Delete")

        if remove:
            
            mycursor.execute(f"Delete from Biz where name='{name_select}' AND designation='{designation_select}'")
            mydb.commit()
            st.warning("Deleted")
