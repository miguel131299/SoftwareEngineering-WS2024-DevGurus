import io
import boto3
import hdx
from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.utilities.downloader import Download
from hdx.utilities.easy_logging import setup_logging

import requests
import os

s3_bucket = "devgurus-raw-data"
s3 = boto3.client("s3")
s3_resource = boto3.resource("s3")


def lambda_handler(event, context):
    setup_logging()
    Configuration.create(hdx_site="stage", user_agent="WFP_Project", hdx_read_only=True)
    download_data_south_america()

    return {
        "statusCode": 200,
        "body": "Files downloaded and uploaded to S3 successfully",
    }


def download_data_south_america():
    download_all_resources_for_dataset("ccb9dfdf-b432-4d50-bd19-ac5616a0447b", "Colombia")


def download_data_africa():
    download_all_resources_for_dataset("319dd40f-c0f8-4f6d-9a8e-9acf31007dd5", "Sudan")


def download_all_resources_for_dataset(dataset_id, country_name):
    dataset = Dataset.read_from_hdx(dataset_id)
    resources = Dataset.get_all_resources([dataset])
    path = "/tmp/" + country_name + "/"
    for resource in resources:
        download_url = resource.data.get("url", None)
        file_name = resource.data.get("name", None)
        file_type = resource.get_file_type()
        file_extension = "." + file_type

        # Check if file type is contained in the name
        # If not the case, then add it
        if not file_extension in file_name:
            file_name = file_name + file_extension

        file_path = os.path.join(path, file_name)

        response = requests.get(download_url)
        if response.status_code == 200:
            s3_resource.Object(s3_bucket, file_path).put(Body=response.content)

        # url, path = resource.download(path)
        # print("Resource URL %s downloaded to %s\n" % (download_url, path))
