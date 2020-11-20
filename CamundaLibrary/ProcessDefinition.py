# robot imports
from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger

# python imports
from typing import Dict
import requests
import json

# local imports
from CamundaLibrary.CamundaResources import CamundaResources


@library
class ProcessDefinition:

    def __init__(self, camunda_engine_url: str = None):
        self._shared_resources = CamundaResources()
        if camunda_engine_url:
            self.set_camunda_url(camunda_engine_url)

    @keyword("Set Camunda URL")
    def set_camunda_url(self, url: str):
        """
        Sets url for camunda eninge. Only necessary when URL cannot be set during initialization of this library or
        you want to switch camunda url for some reason.
        """
        if not url:
            raise ValueError('Cannot set camunda engine url: no url given.')
        self._shared_resources.camunda_url = f'{url}/engine-rest'

    @keyword("Start process")
    def start_process(self, process_key: str, variables: Dict = None):
        """
        Starts a new process instance from a process definition with given key.
        """
        endpoint = f'{self._shared_resources.camunda_url}/process-definition/key/{process_key}/start'

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
