# airflow_plugins


```python
from operators.wecom_operator import failure_callback_wecom

args={ 
    'on_failure_callback': failure_callback_wecom,
    'owner': 'test',
    'email': ['test@test.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 0,
}


with DAG(
    dag_id='test',
    default_args=args,
    schedule_interval='0 * * * * *',
    start_date=days_ago(1),
    tags=['test'],
) as dag:

    task1 = PythonOperator(
        task_id = 'test',
        python_callable = app,
        op_kwargs = {'app': 'test'},
        dag = dag,
    )
```