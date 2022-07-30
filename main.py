import streamlit as st
import requests
import os
import json


st.set_page_config(page_title="DataPerf Evaluation", page_icon="🔎",
                   layout="wide", initial_sidebar_state="collapsed")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/piyush/Downloads/airflow-gcp.json"
if 'if_logged' not in st.session_state:
    st.session_state['if_logged'] = False
    st.session_state['access_token'] = ''

logout_button = st.button(label='Logout', disabled=False)

if logout_button:
    st.session_state['if_logged'] = False

if st.session_state['if_logged'] == False:
    st.markdown("""
                # Welcome to DataPerf Evaluation,
                ## Login to Continue
                """)
    with st.form(key='login', clear_on_submit=True):
        username = st.text_input('Your Email ✉️')
        password = st.text_input("Your Password", type="password")
        submit = st.form_submit_button("Submit")
        if submit:
            with st.spinner('Sending ...'):
                # TODO: Change URL
                url = "https://maasapi.anandpiyush.com/login"
                payload = {'username': username, 'password': password}
                response = requests.request("POST", url, data=payload)
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    st.session_state['access_token'] = json_data["access_token"]
                    st.session_state['if_logged'] = True
                    st.session_state['user_name'] = username
                    st.text("Login Successful")
                    st.experimental_rerun()
                else:
                    st.text("Invalid Credentials ⚠️")

if st.session_state['if_logged'] == True:

    st.markdown("""
    # DataPerf Evaluation
    Welcome to the Interactive Dashboard to submit request for DataPerf offline evaluation.

    ## To use this interface:
    1. Select a ***data_id*** amount the Eight
    2. Select the ***train_size***, default `300`
    3. Select the ***noise_level***, default `0.3`
    4. Select the ***test_size***, default `500`
    5. Select the ***val_size***, default `100`
    6. Select the ***baselines***, default `neighbor_shapley (datascope)`

    ##### The evaluation takes approx 20 mins, report will be sent to your email id.
    
    _Contact support if no email received after 30 mins of sending request referencing run id_
    
    ---
    """)

    tab1, tab2 = st.tabs(["About Report", "Send Request"])

    with tab1:
        st.markdown("""
        # Figure for Each Task

        ##### The x-axis represents the number of data points each algorithm inspects, and the y-axis represents the test accuracy. The black dashed horizontal line represents the initial accuracy without any debugging. Intuitive, the higher the curve, the better the performance - meaning that the debugging algorithm leads to better performance with the same number of inspections.
        
        ---
        """)

        st.image('sample.png')

    with tab2:
        model_name = st.selectbox(
            "Select a data",
            ('01g317-flipped', '04hgtk-flipped', '04rky-flipped',
             '09j2d-flipped', '01g317', '04hgtk', '04rky', '09j2d'),
            key='model_name'
        )

        train_size = st.slider(
            "Select a train_size",
            min_value=0,
            max_value=500,
            step=50,
            value=300,
            key='train_size')

        noise_level = st.slider(
            "Select a noise_level",
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            value=0.3,
            key='noise_level')

        test_size = st.slider(
            "Select a test_size",
            min_value=0,
            max_value=1000,
            step=50,
            value=500,
            key='test_size')

        val_size = st.slider(
            "Select a val_size",
            min_value=0,
            max_value=500,
            step=50,
            value=100,
            key='val_size')

        baselines = st.multiselect(
            "Select one or more baseline",
            options=[
                'neighbor_shapley (datascope)', 'random', 'influence_function', 'mc_shapley'],
            default=['neighbor_shapley (datascope)']
        )

        find_log_btn = st.button("Submit")

        if find_log_btn:
            with st.spinner('Sending ...'):
                url = "http://35.209.64.7:8080/api/v1/dags/DataPerf_v01/dagRuns"
                payload = json.dumps({
                    "conf": {
                        "data_id": model_name,
                        "train_size": train_size,
                        "test_size": test_size,
                        "val_size": val_size,
                        "baselines": "|".join(baselines),
                        "noise_level": int(noise_level*10),
                        "email_param": st.session_state['user_name']
                    }
                })
                headers = {
                    'Content-Type': 'application/json'
                }
                # TODO: Remove
                # os.environ['AIRFLOW_USERNAME'] = '######'
                # os.environ['AIRFLOW_PASSWORD'] = '######'
                # print(payload)

                AIRFLOW_USERNAME = os.getenv('AIRFLOW_USERNAME')
                AIRFLOW_PASSWORD = os.getenv('AIRFLOW_PASSWORD')

                response = requests.request("POST", url, auth=(
                    AIRFLOW_USERNAME, AIRFLOW_PASSWORD), headers=headers, data=payload)
                if response.status_code == 200:
                    json_data = json.loads(response.text)
                    st.success(
                        f"Request Submitted, reference run id :- {json_data['dag_run_id']}")
                else:
                    st.write("Service Unavailable")
