# robot imports
from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger

# generic camunda client
from generic_camunda_client import ApiException, ProcessDefinitionApi, ProcessInstanceWithVariablesDto, StartProcessInstanceDto
import generic_camunda_client

# python imports
from typing import Dict

# local imports
from CamundaLibrary.CamundaResources import CamundaResources


@library(scope='GLOBAL')
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

        variables must be a dictionary like: {'key' : 'value'}
        """
        with self._shared_resources.api_client as api_client:
            api_instance: ProcessDefinitionApi = generic_camunda_client.ProcessDefinitionApi(api_client)
            openapi_variables = CamundaResources.convert_dict_to_openapi_variables(variables)
            start_process_instance_dto: StartProcessInstanceDto = {'variables': openapi_variables}

            try:
                response: ProcessInstanceWithVariablesDto = api_instance.start_process_instance_by_key(
                    key=process_key,
                    start_process_instance_dto=start_process_instance_dto
                )
            except ApiException as e:
                logger.error(f'Failed to start process {process_key}:\n{e}')
                raise e

        return response.to_dict()
