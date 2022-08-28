import time
from datetime import datetime, timedelta

import requests
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException
from airflow.models import Variable
from google import auth
from google.auth import impersonated_credentials
from google.auth.transport.requests import Request

DEFAULT_ARGS = {"owner": "Tobias Lindert", "email": "tobias.lindert@factor-a.com", "retries": 0}

TAGS = ["cloudrun", "gcp", "containers"]
DESCRIPTION = "DAG for testing CloudRun Jobs"

REGION = Variable.get("gcp_region", default_var=None)
PROJECT = Variable.get("gcp_project", default_var=None)
IMPERSONATION = Variable.get("cloudrun_impersonation", default_var=None)
APP = "currencyupdate"


def _get_credentials(impersonation: str) -> str:
    """
    Retrieves the gcp credentials either from the default auth
    or uses impersonation if the impersonation parameter is present
    Args:
        impersonation: The email of the impersonated Service Account
    Returns:
        token: Access Token for GCP

    """
    credentials, _ = auth.default()

    if impersonation is not None:
        target_scopes = ["https://www.googleapis.com/auth/cloud-platform"]

        credentials = impersonated_credentials.Credentials(
            source_credentials=credentials,
            target_principal=impersonation,
            target_scopes=target_scopes,
            lifetime=500,
        )

    credentials.refresh(Request())
    return credentials.token


def _gen_header(access_token: str) -> dict:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }


@dag(
    dag_id="currencyupdate_dag_v2",
    schedule_interval=None,
    start_date=datetime(2022, 8, 17),
    default_args=DEFAULT_ARGS,
    tags=TAGS,
    description=DESCRIPTION,
)
def run_dag():
    @task()
    def start_cloudrun_execution(job_name: str, impersonation: str) -> str:
        """
        Triggers the Execution of a specific Cloud Run Job
        Args:
            job_name: The ID(Name) of the CloudRun Job to be triggered
            impersonation: The email of the impersonated Service Account
        Returns:
            The execution_id of the Cloud Run Job

        """
        r = requests.post(
            f"https://{REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/{PROJECT}/jobs/{job_name}:run",
            headers=_gen_header(_get_credentials(impersonation)),
        )

        if r.status_code != 200:
            raise AirflowFailException("Bad response from API:", r.content)

        return r.json()["metadata"]["name"]

    @task(execution_timeout=timedelta(minutes=60))
    def check_cloudrun_execution(execution_id: str, impersonation: str):
        """
        Monitors the execution of a Cloud Run Job
        Args:
            execution_id: The Execution ID of the previously triggered Cloud Run Job
            impersonation: The email of the impersonated Service Account
        """
        while True:
            r = requests.get(
                f"https://{REGION}-run.googleapis.com/apis/run.googleapis.com/v1"
                f"/namespaces/{PROJECT}/executions/{execution_id}",
                headers=_gen_header(_get_credentials(impersonation)),
            )

            if r.status_code != 200:
                raise AirflowFailException("Bad response from API:", r.content)

            status = r.json()["status"]["conditions"][0]["status"]

            if status == "Unknown":
                print("Deployment Status:", r.json()["status"]["conditions"][0]["message"])
                print("Retrying in 60 seconds ...")
                time.sleep(60)
                continue
            elif status == "False":
                print(r.json()["status"]["conditions"][0]["message"])
                print(r.json()["status"]["logUri"])
                raise AirflowFailException("CloudRun Job Failed")
            elif status == "True":
                break
            else:
                raise AirflowFailException("unknown status")

    execution_id = start_cloudrun_execution(job_name=APP, impersonation=IMPERSONATION)
    check_cloudrun_execution(execution_id=execution_id, impersonation=IMPERSONATION)


start = run_dag()