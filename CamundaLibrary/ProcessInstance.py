# robot imports
from robot.api.deco import keyword, library
from robot.api.logger import librarylogger as logger

# generic camunda client
from generic_camunda_client import ApiException, ProcessInstanceApi, ProcessInstanceDto
import generic_camunda_client

# python imports
from typing import List

# local imports
from CamundaLibrary.CamundaResources import CamundaResources


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
        with self._shared_resources.api_client as api_client:
            api_instance = generic_camunda_client.ProcessInstanceApi(api_client)

            try:
                api_instance.delete_process_instance(id=process_instance_id)
            except ApiException as e:
                logger.error(f'Failed to delete process instance {process_instance_id}:\n{e}')
                raise e

    @keyword("Get all active process instances")
    def get_all_process_instances(self, process_definition_key):
        """
        Returns a list of process instances that are active for a certain process definition identified by key.
        """
        with self._shared_resources.api_client as api_client:
            api_instance: ProcessInstanceApi = generic_camunda_client.ProcessInstanceApi(api_client)

            try:
                response: List[ProcessInstanceDto] = api_instance.get_process_instances(
                    process_definition_key=process_definition_key,
                    active=True
                )
            except ApiException as e:
                logger.error(f'Failed to get process instances of process {process_definition_key}:\n{e}')
                raise e

        return [process_instance.to_dict() for process_instance in response]

