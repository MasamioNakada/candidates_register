import re
import requests

import streamlit as st

base_url = st.secrets["backend"]["base_url"]
access_token = st.secrets["backend"]["access_token"]

def validate_email(email:str):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+'
    
    if re.match(patron, email):
        return True
    else:
        return False

spanish = {
    "general_information":"Información General",
    "available_positions":"Posiciones Disponibles",
    "first_name":"Primer Nombre",
    "middle_name":"Segundo Nombre",
    "last_name":"Apellidos",
    "gender":"Género",
    "gender_options":("Masculino", "Femenino", "Otros","Prefiero no decirlo"),
    "contact_information":"Información de Contacto",
    "email":"Email",
    "country_code":"Código del Pais",
    "phone_number":"Número de celular",
    "enter_cv":"Ingrese su Cv",
    "cover_letter":"Carta de intención"
}
inglish = {
    "general_information":"General Information",
    "available_positions":"Available Positions",
    "first_name":"First Name",
    "middle_name":"Middle Name",
    "last_name":"Last Name",
    "gender":"Gender",
    "gender_options":("Male", "Female", "Others","I prefer not to say it"),
    "contact_information":"Contact Information",
    "email":"Email",
    "country_code":"Country code",
    "phone_number":"Phone Number",
    "enter_cv":"Enter your Cv",
    "cover_letter":"Cover Letter"
}



def main():
    st.set_page_config(
        page_title="superlearner", 
        page_icon="📚", 
        layout="centered", 
        initial_sidebar_state="auto", 
        menu_items=None
    )
    metadata = st.experimental_get_query_params()

    lenguaje = metadata.get("l","en")

    form_id = metadata.get("id",["0"])

    if lenguaje == ["es"]:
        leng = spanish
    else :
        leng = inglish

    
    form_info = requests.get(
        url=f"{base_url}/candidates/info_form",
        params={
            "id":form_id[0]
        }
    ).json()

    st.image(
        "https://images.squarespace-cdn.com/content/v1/58c6ff9020099eded16f3c56/1496321869663-D4J5LPUFOT1KM3R3OZJB/logo.png",
        use_column_width="always",
    )

    st.title(f':orange[{form_info.get("title")}]')
    st.write(form_info.get("description"))

    with st.form("my_form"):
        if form_id == ["0"]:
            global position
            positions = requests.get(f"{base_url}/candidates/positions").json()["positions"]
            clean_positions = []
            for pos in positions:
                if pos["status"]:
                    clean_positions.append(pos["position"])

            st.subheader(f':blue[{leng["available_positions"]}]')
            positionn = st.selectbox(
                f'{leng["available_positions"]}',
                clean_positions,
                index=None,
                placeholder="Choose the Position ..."
            )
            
            for pos in positions:
                
                if pos["position"] == positionn:
                    form_id = [pos["id"]]
            
        if form_id != "default":
            position = ["1"]
        st.subheader(f':blue[{leng["general_information"]}]')
        first_name = st.text_input(leng["first_name"])
        middle_name = st.text_input(leng["middle_name"])
        last_name = st.text_input(leng["last_name"])
        gender = st.selectbox(
            leng["gender"], leng["gender_options"], index=None, placeholder="Choose your gender ..."
        )

        st.divider()
        st.subheader(f':blue[{leng["contact_information"]}]')
        email = st.text_input(leng["email"])
        country_code = st.text_input(leng["country_code"],placeholder="51",)
        phone_number = st.text_input(leng["phone_number"], placeholder="999999999")

        st.divider()
        curriculum = st.file_uploader(leng["enter_cv"], type=["pdf"])
        cover_letter = st.text_area(leng["cover_letter"],max_chars=50000)

        submitted = st.form_submit_button("Submit")
        if submitted:
            # Required Fiedls
            required = {
                "First Name":first_name, 
                "Last Name":last_name,
                "Email": email, 
                "Phone Number":phone_number,
                "Available Position":position,
                "Country Code":country_code
            }
            error_r = []

            for element in required.keys():
                if required[element] == "" or required[element] == None:
                    error_r.append(f"{element} is required")
            del required

            #email verification
            if not validate_email(email):
                error_r.append("Invalid email")

            #phone_nomber verification
            if not phone_number.isdigit():
                error_r.append("Invalid phone number")

            try:
                curriculum.getvalue()
            except:
                error_r.append("Cv is required")

            if len(error_r) != 0:
                st.error("Your form is not submmited 😱")
                for e in error_r:   
                    st.error(f"Error: {e}")
            
            else:
                try:
                    res = requests.post(
                        url=f"{base_url}/candidates/register",
                        files={
                            "form_id":(None,form_id[0]),
                            "first_name":(None,first_name),
                            "middle_name":(None,middle_name),
                            "last_name":(None,last_name),
                            "gender":(None,gender),
                            "email":(None,email),
                            "country_code":(None,country_code),
                            "phone_number":(None,phone_number),
                            "cv": (curriculum.name, curriculum.getvalue()),
                            "cover_letter":(None,cover_letter)
                        }
                    )
                except Exception as e:
                    print(e)
                    st.error("Error in the requests")

                st.success("Your form has been uploaded")
        

if __name__ == "__main__":
    main()
