# robot imports
from robot.api.deco import keyword, library
from robot.api.logger import librarylogger as logger

# python imports
import requests
import json

# local imports
from CamundaLibrary import CamundaResources


@library(scope='GLOBAL', version='0.3.4')
class ProcessInstance:

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

    @keyword("Delete process instance")
    def delete_process_instance(self, process_instance_id):
        """
        USE WITH CARE: Deletes a process instance by id. All data in this process instance will be lost.
        """
        endpoint = f'{self._shared_resources.camunda_url}/process-instance/{process_instance_id}'

        logger.debug(f"Requesting deletion of process instance:\t{process_instance_id}")

        response = requests.delete(endpoint, timeout=(3.05, 15))

        logger.debug(f"Response {response.status_code}")
        response.raise_for_status()

    @keyword("Get all active process instances")
    def get_all_process_instances(self, process_definition_key):
        """
        Returns a list of process instances that are active for a certain process definition identified by key.
        """
        endpoint = f'{self._shared_resources.camunda_url}/process-instance?processDefinitionKey={process_definition_key}&active=true'

        logger.debug(f"Requesting all active instances of process:\t{process_definition_key}")

        response = requests.get(endpoint, timeout=(3.05, 15))

        logger.debug(f"Response {response.status_code}")
        response.raise_for_status()
        return json.loads(response.content)

