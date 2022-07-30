# Assignment_04

## Links:

* Airflow - [UI](http://35.209.64.7:8080/home)
  Deployed on Google Compute Engine
* Streamlit - [UI](https://bigdataia-summer2022-team04-assignment-04-main-streamlit-1m1gti.streamlitapp.com/)
  Deployed on Streamlit Cloud

---

## Architecture:

![Architecture](/assets/arch_v1.png)

---

## Part 1: Automating Benchmarking of datasets

* DataPerf Source Source code and dataset stored as a branch [dataperf_src](https://github.com/BigDataIA-Summer2022-Team04/Assignment_04/tree/dataperf_src)

* Airflow DAG
  * `clean_dir` - Clean's the working directory 
  * `download_code` - Download's the source code along with dataset from [dataperf_src](https://github.com/BigDataIA-Summer2022-Team04/Assignment_04/tree/dataperf_src) branch
  * `generate_template` - Generates the `task_setup.yml` file from the `template.yml` file replacing the user input.
  * `run_python_script` - Runs the computation script namely `create_baselines.py`, `main.py` and `plotter.py`
  * `send_report_email` - Send an email along with the generated report image 
  * `send_failure_email` - Send an email informing the failure of job
  * `send_ack_email` - Send an email acknowledging the job run and for for further update email

## Screenshots:
### 1. Airflow DAG's
![Airflow DAG's](/assets/airflow_dag.png)

### 2. Template file - [link](https://github.com/BigDataIA-Summer2022-Team04/Assignment_04/blob/dataperf_src/template.yml)
```yaml
paths:
embedding_folder: embeddings/
groundtruth_folder: data/
submission_folder: submissions/
results_folder: results/

tasks:
- data_id: {{ data_id }}
    train_size:  {{ train_size }}
    noise_level:  {{ noise_level }}
    test_size:  {{ test_size }}
    val_size:  {{ val_size }}

baselines:
    {% for element in  baselines %}
    - name: {{ element }}
    {% endfor %}
```

### 3. Streamlit UI
![Streamlit UI](/assets/streamlit.png)

### 4. Job Run Acknowledgement Email
![Acknowledgement Email](/assets/ack.png)

### 5. Job Run Report Email
![Report Email](/assets/report.png)

### 6. Job Run Failure Email
![Failure Email](/assets/failure.png)

### 7. Report Sample
![Sample Report](/assets/attachment.png)


---


## Part 2: Technology evaluation
Snoopy Observation recorded [here](https://github.com/BigDataIA-Summer2022-Team04/Assignment_04/tree/snoopy)


---


## Git Branches:
* [airflow](https://github.com/BigDataIA-Summer2022-Team04/Assignment_04/tree/airflow) - Airflow Setup and DAG
* [dataperf_src](https://github.com/BigDataIA-Summer2022-Team04/Assignment_04/tree/dataperf_src) - DataPerf Source Code and Dataset
* [Snoopy](https://github.com/BigDataIA-Summer2022-Team04/Assignment_04/tree/snoopy) - Snoopy observation
* [Streamlit](https://github.com/BigDataIA-Summer2022-Team04/Assignment_04/tree/streamlit) - Streamlit User Interface

