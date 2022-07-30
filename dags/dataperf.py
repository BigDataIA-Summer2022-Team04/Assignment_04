import os 
import glob
import base64
import time
import numpy as np
import pandas as pd
import tensorflow as tf
import urllib.request
import shutil
from airflow.models import DAG
from airflow.models.param import Param
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from jinja2 import Environment, FileSystemLoader
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)


args = {
 
    'owner': 'Anku',
    'start_date': days_ago(0),
    'email': ['anand.pi@northeastern.edu'],
	'email_on_failure': True
}

user_input = {
        "data_id": Param('01g317-flipped', type='string', minLength=2, maxLength=250),
        "train_size": Param(300, type='integer', minimum=0, maximum=500),
        "test_size": Param(500, type='integer', minimum=0, maximum=500),
        "val_size": Param(100, type='integer', minimum=0, maximum=500),
        "baselines": Param('neighbor_shapley (datascope)', type='string', minLength=2, maxLength=250),
        "noise_level": Param(3, type='integer', minimum=0, maximum=5),
        'email_param': Param(
        default='anand.pi@northeastern.edu',
        type='string',
        format='idn-email',
        minLength=5,
        maxLength=255,
    ),}
 
dag = DAG(dag_id = 'DataPerf_v01',
            default_args=args,
            params=user_input,
        )

def generate_template(**kwargs):
    data_id= kwargs['dag_run'].conf['data_id']
    train_size= kwargs['dag_run'].conf['train_size']
    noise_level= kwargs['dag_run'].conf['noise_level'] / 10
    test_size= kwargs['dag_run'].conf['test_size']
    val_size= kwargs['dag_run'].conf['val_size']
    baseline= kwargs['dag_run'].conf['baselines']

    baselines = baseline.split('|')

    values = {
        'data_id': data_id,
        'train_size': train_size,
        'noise_level': noise_level,
        'test_size': test_size,
        'val_size': val_size,
        'baselines': baselines,
        }
    env = Environment(loader = FileSystemLoader('/opt/airflow/working_data/Assignment_04'),   trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('template.yml')
    file=open("/opt/airflow/working_data/Assignment_04/task_setup.yml", "w")
    file.write(template.render(values))
    file.close()
    print(template.render(values))


def send_report_email(**kwargs):
    # TODO: Remove the API KEY
    os.environ['SENDGRID_API_KEY'] = "############################" 
    ts = time.strftime("%Y-%m-%d_%H:%M:%S")
    run_id = str(kwargs['dag_run']).split(',')[0].split(' ')[-1]

    message = Mail(
        from_email='anand.pi@northeastern.edu',
        to_emails=kwargs['dag_run'].conf['email_param'],
        subject=f"DataPerf | {run_id}",
        html_content=f"""
<head>
</head>
<body>
   <h1 style="text-align:center;">DataPerf Evaluation Report</h1>
   <h4 style="text-align:left;">Figure for Each Task </h4>
   <p> The x-axis represents the number of data points each algorithm inspects, and the y-axis represents the test accuracy. The black dashed horizontal line represents the initial accuracy without any debugging. Intuitive, the higher the curve, the better the performance - meaning that the debugging algorithm leads to better performance with the same number of inspections. </p>
   <p> <i> Report generated on {ts} </i> </p>
</body>
""")
    os.chdir('/opt/airflow/working_data/Assignment_04/results')
    filename = glob.glob("*.png")
    with open(filename[0], 'rb') as f:
        data = f.read()
        f.close()
    encoded_file = base64.b64encode(data).decode()

    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName('attachment.png'),
        FileType('image/png'),
        Disposition('attachment')
    )
    message.attachment = attachedFile
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
    

def send_ack_email(**kwargs):
    run_id = str(kwargs['dag_run']).split(',')[0].split(' ')[-1]
    # TODO: Remove the API KEY
    os.environ['SENDGRID_API_KEY'] = "############################"
    ts = time.strftime("%Y-%m-%d_%H:%M:%S")

    message = Mail(
        from_email='anand.pi@northeastern.edu',
        to_emails=kwargs['dag_run'].conf['email_param'],
        subject=f"DataPerf | {run_id}",
        html_content=f"""
<head>
</head>
<body>
   <h1 style="text-align:center;">DataPerf Evaluation Request</h1>
   <h4 style="text-align:left;"> RunId: {run_id}</h4>
   <p> This is to acknowledgement your request and you should receive the report once processed </p>
   <p> <i> Email generated on {ts} </i> </p>
</body>
""")

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def send_failure_email(**kwargs):
    run_id = str(kwargs['dag_run']).split(',')[0].split(' ')[-1]
    # TODO: Remove the API KEY
    os.environ['SENDGRID_API_KEY'] = "############################"
    ts = time.strftime("%Y-%m-%d_%H:%M:%S")

    message = Mail(
        from_email='anand.pi@northeastern.edu',
        to_emails=kwargs['dag_run'].conf['email_param'],
        subject=f"DataPerf | {run_id}",
        html_content=f"""
<head>
</head>
<body>
   <h1 style="text-align:center;">DataPerf Evaluation Request</h1>
   <h4 style="text-align:left;"> RunId: {run_id}</h4>
   <p> This is update that your request failed, kindly request a new one or contact support </p>
   <p> <i> Email generated on {ts} </i> </p>
</body>
""")

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


with dag:

    clean_dir = BashOperator(
        task_id="clean_dir",
        bash_command='echo "Cleaning following files" ; ls -l /opt/airflow/working_data ; rm -rf /opt/airflow/working_data/*',
    )

    download_code = BashOperator(
        task_id="download_code",
        bash_command='echo "Downloading the DataPerf Source Code" ; cd /opt/airflow/working_data ; git clone --branch dataperf_src https://github.com/BigDataIA-Summer2022-Team04/Assignment_04.git',
    )

    generate_template = PythonOperator(
        task_id='generate_template',
        python_callable = generate_template,
        provide_context=True,
        dag=dag,
    )

    run_python_script = BashOperator(
        task_id="run_python_script",
        bash_command='echo "Running python script" ; cd /opt/airflow/working_data/Assignment_04 ; python3 create_baselines.py && python3 main.py && python3 plotter.py',
    )

    send_report_email = PythonOperator(
        task_id='send_report_email',
        python_callable = send_report_email,
        provide_context=True,
        dag=dag,
        trigger_rule='all_success'
    )

    send_ack_email = PythonOperator(
        task_id='send_ack_email',
        python_callable = send_ack_email,
        provide_context=True,
        dag=dag,
    )

    send_failure_email = PythonOperator(
        task_id='send_failure_email',
        python_callable = send_failure_email,
        provide_context=True,
        dag=dag,
        trigger_rule='one_failed'
    )

    clean_dir >> download_code >> generate_template >> run_python_script >> [send_report_email, send_failure_email]
    generate_template >> send_ack_email
    