from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger
from typing import List
import requests
import json


@library(scope='GLOBAL')
class ProcessDefinition:

    CAMUNDA_HOST = None

    def __init__(self, camunda_host: str = ''):
        self.CAMUNDA_HOST = camunda_host

    @keyword("Set Camunda URL")
    def set_camunda_url(self, url: str):
        """
        Sets url for camunda eninge. Only necessary when URL cannot be set during initialization of this library or
        you want to switch camunda url for some reason.
        """
        if not url:
            raise ValueError('Cannot set camunda engine url: no url given.')
        self.CAMUNDA_HOST = url

    @keyword("Start process")
    def start_process(self, process_key: str, variables: List = None):
        endpoint = f'{self.CAMUNDA_HOST}/engine-rest/process-definition/key/{process_key}/start'

        header = {
            'Content-type': 'application/json'
        }

        json_body = { }

        if variables:
            json_body["variables"]=variables

        logger.info(f"Request:\t{json_body}")

        response = requests.post(endpoint,
                            data=json.dumps(json_body),
                            headers=header, timeout=(3.05, 15))

        logger.debug(f"Response {response.status_code}:\t{response.content}")
        response.raise_for_status()

        return json.loads(response.content)
