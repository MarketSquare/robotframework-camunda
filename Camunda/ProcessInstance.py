from robot.api.deco import keyword, library
from robot.api.logger import librarylogger as logger
import requests
import json


@library(scope='GLOBAL')
class ProcessInstance:
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

    @keyword("Delete process instance")
    def delete_process_instance(self, process_instance_id):
        endpoint = f'{self.CAMUNDA_HOST}/engine-rest/process-instance/{process_instance_id}'

        logger.debug(f"Requesting deletion of process instance:\t{process_instance_id}")

        response = requests.delete(endpoint, timeout=(3.05, 15))

        logger.debug(f"Response {response.status_code}")
        response.raise_for_status()

    @keyword("Get all active process instances")
    def get_all_process_instances(self, process_definition_key):
        endpoint = f'{self.CAMUNDA_HOST}/engine-rest/process-instance?processDefinitionKey={process_definition_key}&active=true'

        logger.debug(f"Requesting all active instances of process:\t{process_definition_key}")

        response = requests.get(endpoint, timeout=(3.05, 15))

        logger.debug(f"Response {response.status_code}")
        response.raise_for_status()
        return json.loads(response.content)

