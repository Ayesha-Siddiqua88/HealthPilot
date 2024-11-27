import pickle
import pandas as pd
import streamlit as st
import gspread
import plotly.graph_objects as go
import plotly.express as px
# import openai

from streamlit_option_menu import option_menu
from google.oauth2 import service_account
from datetime import datetime

# load_dotenv()
# api_key= os.getenv("OPENAI_API_KEY")
# openai.api_key = api_key

# styling
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.unsplash.com/photo-1554120013-4ba50c1a1788?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
background-size: 180%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}}
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# diabetes section
# storing data in diabetes google sheets
def store_data_in_google_sheets(data):
    json_file_path = 'Diabetes.json'
    credentials = service_account.Credentials.from_service_account_file(
        json_file_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    )
    client = gspread.authorize(credentials)
    sheet = client.open("Diabetes spreadsheet").sheet1  
    date = pd.to_datetime('today').strftime("%Y-%m-%d")
    data_with_date = [date] + data
    sheet.append_row(data_with_date)


if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()


# insert data into diabetes table
def insert_data(data):
    try:
        json_file_path = 'Diabetes.json'
        credentials = service_account.Credentials.from_service_account_file(
        json_file_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(credentials)
        sheet = client.open("Diabetes spreadsheet").sheet1  
        current_date = datetime.now().strftime("%Y-%m-%d")
        data_with_date = [current_date] + data
        sheet.append_row(data_with_date) 
    except Exception as e:
        st.error(f"Error inserting data: {e}")


# Function to fetch data from Google Sheets based on the selected period
def fetch_data(selected_start_date, selected_end_date):
    sheet = client.open("Diabetes spreadsheet").sheet1 
    all_data = sheet.get_all_records()

    df = pd.DataFrame(all_data)

    df['Date'] = pd.to_datetime(df['Date'])
    mask = (df['Date'] >= selected_start_date) & (df['Date'] <= selected_end_date)
    selected_data = df.loc[mask].drop('diab_diagnosis', axis=1)

    return selected_data


def get_google_sheets_data(sheet_name, json_file):
    creds = service_account.Credentials.from_service_account_file(json_file,
                                                                  scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                                                                  )
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    return data

# loading the trained ml models
diabetes_model = pickle.load(open('Model/diabetes_model.sav', 'rb'))
heart_disease_model=pickle.load(open('Model/heart_disease_model.sav','rb'))

# main sidebar
with st.sidebar:
    selected = option_menu(menu_title=None,
                        options=['Diabetes Analyser', 'Heart Disease Analyser'],
                        menu_icon='hospital-fill',
                        icons=['activity',  'heart'],
                        default_index=0)
    st.image("images/Logo.png")

# Diabetes Prediction Page sidebar
if selected == 'Diabetes Analyser':
    select = option_menu(menu_title=None,
                        options=['Diabetes Report',
                        'Diabetes Analysis'],
                        icons=['pencil-fill','bar-chart-fill'],
                        orientation='horizontal',
                        )
    # if select == 'Chatbot':
    #         chatbot_section("Diabetes") 

# Heart Prediction Page sidebar
if selected == 'Heart Disease Analyser':
    select = option_menu(menu_title=None,
                        options=['Heart Report',
                        'Heart Analysis'],
                        icons=['pencil-fill','bar-chart-fill'],
                        orientation='horizontal',
                        )
    # if select == 'Chatbot':
    #         chatbot_section("Heart Disease")       


def diabetes_report(user_data):
    normal_values = {
        "Glucose": (70, 140),  # mg/dL (fasting and post-meal)
        "BloodPressure": (80, 120),  # mmHg
        "SkinThickness": (0, 35),  # mm
        "Insulin": (0, 200),  # U/mL
        "BMI": (18.5, 24.9),  # kg/m^2
        "DiabetesPedigreeFunction": (0, 1.5),  # Range based on family history
    }

    report = []

    user_data = {key: float(value) if isinstance(value, str) else value for key, value in user_data.items()}

    for key, value in user_data.items():
        if key in normal_values:
            min_value, max_value = normal_values[key]
            if value < min_value:
                report.append(f"{key}: {value} (Low - Risky). Minimum value should be {min_value}")
            elif value > max_value:
                report.append(f"{key}: {value} (High - Risky). Maximum value should be {max_value}")
            else:
                report.append(f"{key}: {value} (Normal)")
        else:
            report.append(f"{key}: {value} (No standard value available)")

    report.append("\n### **Precautions:**")

    report.append("- **Healthy Eating:** Focus on a balanced diet with whole grains, lean proteins, and plenty of vegetables. Limit processed foods and sugary drinks.")
    report.append("- **Exercise:** Regular physical activity, such as 30 minutes of moderate exercise daily (e.g., walking, cycling, swimming), can help maintain a healthy weight and improve insulin sensitivity.")
    report.append("- **Stress Management:** Practice stress-reduction techniques such as deep breathing, meditation, or yoga to improve overall well-being and avoid stress-induced blood sugar spikes.")

    # report.append("\n### **Conclusion**:")
    # if user_data["Glucose"] > 140 or user_data["BMI"] > 30 or user_data["Insulin"] > 200:
    #     report.append("Your results suggest you might be at risk of developing diabetes. Please consider consulting with a healthcare provider for further evaluation.")
    # else:
    #     report.append("Your results are within normal ranges. Continue to follow a healthy lifestyle to maintain your health.")

    for line in report:
        st.markdown(f"- {line}")


# Diabetes Report entry
if select=='Diabetes Report':
    st.write("In the Diabetes Report section, you can enter various health parameters to receive an assessment of your diabetes status. "
             "Based on the input, we’ll provide a recommendation to help you understand your current health condition.")
    with st.form("entry_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                Pregnancies = st.text_input('Number of Pregnancies')

            with col2:
                Glucose = st.text_input('Glucose Level')

            with col3:
                BloodPressure = st.text_input('Blood Pressure value')

            with col1:
                SkinThickness = st.text_input('Skin Thickness value')

            with col2:
                Insulin = st.text_input('Insulin Level')

            with col3:
                BMI = st.text_input('BMI value')

            with col1:
                DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')

            with col2:
                Age = st.text_input('Age of the Person')


            diab_diagnosis = ''
            submitted=st.form_submit_button('Diabetes Test Result')
            if submitted:
        
                user_input = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                            BMI, DiabetesPedigreeFunction, Age]

                user_input = [float(x) for x in user_input]

                diab_prediction = diabetes_model.predict([user_input])

                if diab_prediction[0] == 1:
                    diab_diagnosis = 'According to the results, you show signs that could indicate a potential risk of developing diabetes.'
                else:
                    diab_diagnosis = 'The results suggest that you currently show no signs of diabetes. However, regular check-ups and a healthy lifestyle are still important to maintain this status.'

                data_to_insert = [Pregnancies, Glucose, BloodPressure,SkinThickness, Insulin,BMI, DiabetesPedigreeFunction,Age,diab_diagnosis] 
                insert_data(data_to_insert)

                st.session_state.diabetes_data = {
                    "Pregnancies": Pregnancies,
                    "Glucose": Glucose,
                    "BloodPressure": BloodPressure,
                    "SkinThickness": SkinThickness,
                    "Insulin": Insulin,
                    "BMI": BMI,
                    "DiabetesPedigreeFunction": DiabetesPedigreeFunction,
                    "Age": Age,
                    "Diagnosis": diab_diagnosis
                }

                st.success(diab_diagnosis)
                if hasattr(st.session_state, 'diabetes_data'):
                    diabetes_data = pd.DataFrame(st.session_state.diabetes_data, index=[0])
                    st.dataframe(diabetes_data)
                    fig = go.Figure(data=[go.Pie(labels=diabetes_data.columns, values=diabetes_data.iloc[0].values)])
                    st.plotly_chart(fig, use_container_width=True)

                diabetes_report({
                    "Glucose": Glucose,
                    "BloodPressure": BloodPressure,
                    "SkinThickness": SkinThickness,
                    "Insulin": Insulin,
                    "BMI": BMI,
                    "DiabetesPedigreeFunction": DiabetesPedigreeFunction,
                })

                    
# Diabetes Analysis section
if select=='Diabetes Analysis':

    st.write("In the Diabetes Analysis section, you can view trends and patterns in your diabetes-related health data over time. "
             "Select a time period to analyze how key health indicators have changed.")

    json_file_path = 'Diabetes.json'
    credentials = service_account.Credentials.from_service_account_file(
        json_file_path,
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(credentials)

    all_data = fetch_data(pd.to_datetime('2024-11-03'), pd.to_datetime('2024-12-30')) 

    if all_data.empty:
        st.warning("No data available.")
    else:
        unique_dates = sorted(all_data['Date'].dt.strftime('%Y-%m-%d').unique())

    if not unique_dates:
        st.warning("No unique dates found.")
    else:
        start_date = st.selectbox("Select Start Date:", unique_dates)
        end_date = st.selectbox("Select End Date:", unique_dates)

        selected_starting_date = pd.to_datetime(start_date)
        selected_ending_date = pd.to_datetime(end_date)

        selected_data = fetch_data(selected_starting_date, selected_ending_date)

        st.title("Diabetes Variation")
        st.write(selected_data)

        if selected_data.empty:
            st.warning("No report available for the selected period.")
        else:
            normal_ranges = {
                    "Glucose": (70, 140),  # Glucose levels (mg/dL)
                    "BloodPressure": (80, 120),  # Blood Pressure (mmHg)
                    "BMI": (18.5, 24.9),  # BMI (kg/m²)
                    "Insulin": (15, 276),  # Insulin (µU/mL)
                    "DiabetesPedigreeFunction": (0, 1),  # Diabetes Pedigree Function
                }

            for col in normal_ranges.keys():
                    if col in selected_data.columns:
                        min_val, max_val = normal_ranges[col]

                        fig = px.line(
                            selected_data,
                            x="Date",
                            y=col,
                            title=f"Variation in {col} Over Time",
                        )

                        fig.add_shape(
                            type="rect",
                            xref="paper",
                            yref="y",
                            x0=0, x1=1,
                            y0=min_val, y1=max_val,
                            fillcolor="red",
                            opacity=0.2,
                            line_width=0,
                            layer="below"
                        )

                        fig.update_layout(
                            template='plotly_white',
                            yaxis_title=f"{col} Value",
                            xaxis_title="Date",
                        )
                        st.plotly_chart(fig, use_container_width=True)
            columns_to_plot = ['Glucose','BloodPressure', 'BMI','Insulin','DiabetesPedigreeFunction']
            fig = px.line(selected_data, x='Date', y=columns_to_plot, title='Diabetes Progress Over Time')
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)


# insert data into diabetes table
def insert_data(data):
    try:
        json_file_path = '.Diabetes.json'
        credentials = service_account.Credentials.from_service_account_file(
        json_file_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(credentials)
        sheet = client.open("Diabetes spreadsheet").sheet1  
        current_date = datetime.now().strftime("%Y-%m-%d")
        data_with_date = [current_date] + data
        sheet.append_row(data_with_date) 
    except Exception as e:
        st.error(f"Error inserting data: {e}")

# Heart disease prediction
def store_data_in_google_sheets(data):
    json_file_path = 'Heart.json'
    credentials = service_account.Credentials.from_service_account_file(
        json_file_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    )
    client = gspread.authorize(credentials)
    sheet = client.open("Heart spreadsheet").sheet1  
    date = pd.to_datetime('today').strftime("%Y-%m-%d")
    data_with_date = [date] + data
    sheet.append_row(data_with_date)


if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()


# insert data into diabetes table
def insert_data(data):
    try:
        json_file_path = 'Heart.json'
        credentials = service_account.Credentials.from_service_account_file(
        json_file_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(credentials)
        sheet = client.open("Heart spreadsheet").sheet1  
        current_date = datetime.now().strftime("%Y-%m-%d")
        data_with_date = [current_date] + data
        sheet.append_row(data_with_date) 
    except Exception as e:
        st.error(f"Error inserting data: {e}")


# Function to fetch data from Google Sheets based on the selected period
def fetch_data(selected_start_date, selected_end_date):
    sheet = client.open("Heart spreadsheet").sheet1 
    all_data = sheet.get_all_records()

    df = pd.DataFrame(all_data)

    df['Date'] = pd.to_datetime(df['Date'])
    mask = (df['Date'] >= selected_start_date) & (df['Date'] <= selected_end_date)
    selected_data = df.loc[mask].drop('heart_diagnosis', axis=1)

    sex_mapping = {1: 'Female', 0: 'Male'}
    selected_data['sex'] = selected_data['sex'].map(sex_mapping)
    return selected_data


def heart_report(user_data):
    normal_values = {
        "cp": (0, 3),  # Chest Pain Type (0 to 3, where 0 is asymptomatic)
        "trestbps": (90, 120),  # Resting Blood Pressure in mmHg
        "chol": (125, 200),  # Cholesterol in mg/dL
        "fbs": (0, 1),  # Fasting Blood Sugar (1 = true, 0 = false)
        "restecg": (0, 1),  # Resting Electrocardiographic Results (0 = normal, 1 = abnormal)
        "thalach": (60, 100),  # Maximum Heart Rate Achieved (bpm)
        "exang": (0, 1),  # Exercise-Induced Angina (0 = no, 1 = yes)
        "oldpeak": (0, 2),  # ST Depression Induced by Exercise Relative to Rest
        "slope": (0, 2),  # Slope of the Peak Exercise ST Segment (0 = downsloping, 2 = upsloping)
        "ca": (0, 3),  # Number of Major Vessels Colored by Fluoroscopy (0 to 3)
        "thal": (0, 2),  # Thalassemia (0 = normal, 1 = fixed defect, 2 = reversible defect)
    }
    report = []
    
    user_data = {key: float(value) if isinstance(value, str) else value for key, value in user_data.items()}

    for key, value in user_data.items():
        if key in normal_values:
            min_value, max_value = normal_values[key]
            if isinstance(value, str):
                value = float(value)
            if value < min_value:
                report.append(f"{key.upper()} ({get_fullform(key)}): {value} (Low - Risky, Minimum value should be {min_value})")
            elif value > max_value:
                report.append(f"{key.upper()} ({get_fullform(key)}): {value} (High - Risky, Maximum value should be {max_value})")
            else:
                report.append(f"{key.upper()} ({get_fullform(key)}): {value} (Normal)")

    report.append("\n### **Precautions:**")

    report.append(" **Healthy Eating:** Focus on a heart-healthy diet rich in fruits, vegetables, lean proteins, and whole grains. Limit saturated fats, trans fats, and sodium intake.")
    report.append(" **Exercise:** Engage in at least 30 minutes of moderate physical activity daily, such as walking, cycling, or swimming, to maintain cardiovascular health.")
    report.append(" **Stress Management:** Practice stress-relief techniques like meditation, deep breathing, or yoga to prevent stress-induced heart strain.")

    # report.append("\n### **Conclusion**:")
    # if (
    #     user_data["chol"] > 240
    #     or user_data["trestbps"] > 140
    #     or user_data["thalach"] < 60
    #     or user_data["exang"] == 1
    # ):
    #     report.append(
    #         "You might be at risk of heart disease. Please consult with a healthcare provider for a detailed evaluation."
    #     )
    # else:
    #     report.append(
    #         "Your results are within normal ranges. Continue following a healthy lifestyle to maintain your heart health."
    #     )
    for line in report:
        if line.strip(): 
            st.markdown(f"- {line}")


def get_fullform(parameter):
    fullforms = {
        "cp": "Chest Pain Type",
        "trestbps": "Resting Blood Pressure",
        "chol": "Cholesterol",
        "fbs": "Fasting Blood Sugar",
        "restecg": "Resting Electrocardiographic Results",
        "thalach": "Maximum Heart Rate Achieved",
        "exang": "Exercise-Induced Angina",
        "oldpeak": "ST Depression",
        "slope": "Slope of the Peak Exercise ST Segment",
        "ca": "Number of Major Vessels Colored by Fluoroscopy",
        "thal": "Thalassemia",
    }
    return fullforms.get(parameter, "Unknown Parameter")


# Heart Report entry
if select =='Heart Report':
    st.write("In the Heart Report section, you can enter various health parameters to receive an assessment of your heart status. "
             "Based on the input, we’ll provide a recommendation to help you understand your current health condition.")
    with st.form("entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.text_input('Age')

        with col2:
            sex = st.text_input('Sex')
            if sex.lower() == 'female':
                sex = 1
            elif sex.lower() == 'male':
                sex = 0
            else:
                sex = 0

        with col3:
            cp = st.text_input('Chest Pain Type(0-3)')

        with col1:
            trestbps = st.text_input('Resting Blood Pressure(mm Hg)')

        with col2:
            chol = st.text_input('Serum Cholestoral(mg/dL)')

        with col3:
            fbs = st.text_input('Fasting Blood Sugar (0 = False, 1 = True)')

        with col1:
            restecg = st.text_input('Resting Electrocardiographic(0-1)')

        with col2:
            thalach = st.text_input('Maximum Heart Rate (bpm)')

        with col3:
            exang = st.text_input('Exercise Induced Angina (0 = No, 1 = Yes)')

        with col1:
            oldpeak = st.text_input('ST depression (mm)')

        with col2:
            slope = st.text_input('Slope of the peak exercise ST segment (0-2)')

        with col3:
            ca = st.text_input('Number of Major vessels (0-3)')

        with col1:
            thal = st.text_input('Thalassemia (0 = Normal, 1 = Fixed Defect, 2 = Reversible Defect)')

        heart_diagnosis = ''

        submitted=st.form_submit_button('Heart Test Result')
    if submitted:

        user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]


        user_input = [float(x) for x in user_input]

        heart_prediction = heart_disease_model.predict([user_input])

        if heart_prediction[0] == 1:
            heart_diagnosis = 'According to the results, you show signs that could indicate a potential risk of developing heart disease.'
        else:
            heart_diagnosis = 'The results suggest that you currently show no signs of heart disease. However, regular check-ups and a healthy lifestyle are still important to maintain this status.'

        data_to_insert = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal,heart_diagnosis] 
        insert_data(data_to_insert)

        st.session_state.heart_data = {
            "age":age,
            "sex":sex,
            "cp":cp,
            "trestbps":trestbps,
            "chol":chol,
            "fbs":fbs,
            "restecg":restecg,
            "thalach":thalach,
            "exang":exang,
            "oldpeak":oldpeak,
            "slope":slope,
            "ca":ca,
            "thal":thal,
            "Diagnosis": heart_diagnosis

        }

        st.success(heart_diagnosis)
        if hasattr(st.session_state, 'heart_data'):
            heart_data = pd.DataFrame(st.session_state.heart_data, index=[0])
            st.dataframe(heart_data)
            fig = go.Figure(data=[go.Pie(labels=heart_data.columns, values=heart_data.iloc[0].values)])
            st.plotly_chart(fig, use_container_width=True)

        heart_report({
            "cp":cp,
            "trestbps":trestbps,
            "chol":chol,
            "fbs":fbs,
            "restecg":restecg,
            "thalach":thalach,
            "exang":exang,
            "oldpeak":oldpeak,
            "slope":slope,
            "ca":ca,
            "thal":thal
        })


# Heart Analysis section
if select=='Heart Analysis':

    st.write("In the Heart Analysis section, you can view trends and patterns in your heart-related health data over time. "
             "Select a time period to analyze how key health indicators have changed.")

    json_file_path = 'Heart.json'
    credentials = service_account.Credentials.from_service_account_file(
        json_file_path,
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(credentials)

    all_data = fetch_data(pd.to_datetime('2024-11-24'), pd.to_datetime('2024-12-30')) 

    if all_data.empty:
        st.warning("No data available.")
    else:
        unique_dates = sorted(all_data['Date'].dt.strftime('%Y-%m-%d').unique())

    if not unique_dates:
        st.warning("No unique dates found.")
    else:
        start_date = st.selectbox("Select Start Date:", unique_dates)
        end_date = st.selectbox("Select End Date:", unique_dates)

        selected_starting_date = pd.to_datetime(start_date)
        selected_ending_date = pd.to_datetime(end_date)

        selected_data = fetch_data(selected_starting_date, selected_ending_date)

        st.header("Heart Report Variation")
        st.write(selected_data)

        if selected_data.empty:
            st.warning("No report available for the selected period.")
        else:
            normal_ranges = {
                    "cp": (0, 3),  # Chest Pain Type
                    "trestbps": (90, 120),  # Resting Blood Pressure
                    "chol": (125, 200),  # Cholesterol
                    "fbs": (0, 1),  # Fasting Blood Sugar
                    "restecg": (0, 1),  # Resting ECG Results
                    "thalach": (60, 100),  # Maximum Heart Rate Achieved
                    "exang": (0, 1),  # Exercise-Induced Angina
                    "oldpeak": (0, 2),  # ST Depression
                    "slope": (0, 2),  # Slope of the Peak ST Segment
                    "ca": (0, 3),  # Number of Major Vessels
                    "thal": (0, 2),  # Thalassemia
                }

            for col in normal_ranges.keys():
                    if col in selected_data.columns:
                        min_val, max_val = normal_ranges[col]

                        fig = px.line(
                            selected_data,
                            x="Date",
                            y=col,
                            title=f"Variation in {col.upper()} ({get_fullform(col)}) Over Time",
                        )

                        fig.add_shape(
                            type="rect",
                            xref="paper",
                            yref="y",
                            x0=0, x1=1,
                            y0=min_val, y1=max_val,
                            fillcolor="red",
                            opacity=0.2,
                            line_width=0,
                            layer="below"
                        )

                        fig.update_layout(
                            template='plotly_white',
                            yaxis_title=f"{get_fullform(col)} Value",
                            xaxis_title="Date",
                        )

                        st.plotly_chart(fig, use_container_width=True)

        
            columns_to_plot = ['cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
            fig = px.line(selected_data, x='Date', y=columns_to_plot, title='Heart Progress Over Time')
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
