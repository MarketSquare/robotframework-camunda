# robot imports
from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger

# generic camunda client
from generic_camunda_client import ApiException, ProcessDefinitionApi, ProcessInstanceWithVariablesDto, StartProcessInstanceDto, ProcessInstanceModificationInstructionDto
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
    def start_process(self, process_key: str, variables: Dict = None, files: Dict = None,
                      before_activity_id: str = None, after_activity_id: str = None) -> Dict:
        """
        Starts a new process instance from a process definition with given key.

        variables: _optional_ dictionary like: {'variable name' : 'value'}

        files: _optional_ dictionary like: {'variable name' : path}. will be attached to variables in Camunda

        before_activity_id: _optional_ id of activity at which the process starts before. *CANNOT BE USED TOGETHER WITH _after_activity_id_*

        after_activity_id: _optional_ id of activity at which the process starts after. *CANNOT BE USED TOGETHER WITH _before_activity_id_*

        Returns response from Camunda as dictionary

        == Examples ==
        | `start process`      | apply for job promotion    | _variables_= { 'employee' : 'John Doe', 'permission_for_application_granted' : True}   | _files_ = { 'cv' : 'documents/my_life.md'}  | _after_activity_id_ = 'Activity_ask_boss_for_persmission'   |
        """
        if not process_key:
            raise ValueError('Error starting process. No process key provided.')

        if before_activity_id and after_activity_id:
            raise AssertionError('2 activity ids provided. Cannot start before and after an activity.')

        with self._shared_resources.api_client as api_client:
            api_instance: ProcessDefinitionApi = generic_camunda_client.ProcessDefinitionApi(api_client)
            openapi_variables = CamundaResources.convert_dict_to_openapi_variables(variables)
            openapi_files = CamundaResources.convert_file_dict_to_openapi_variables(files)
            openapi_variables.update(openapi_files)

            start_instructions = None
            if before_activity_id or after_activity_id:
                instruction: ProcessInstanceModificationInstructionDto = ProcessInstanceModificationInstructionDto(
                    type='startBeforeActivity' if before_activity_id else 'startAfterActivity',
                    activity_id=before_activity_id if before_activity_id else after_activity_id
                )
                start_instructions = [instruction]

            start_process_instance_dto: StartProcessInstanceDto = StartProcessInstanceDto(
                variables=openapi_variables,
                start_instructions=start_instructions
            )

            try:
                response: ProcessInstanceWithVariablesDto = api_instance.start_process_instance_by_key(
                    key=process_key,
                    start_process_instance_dto=start_process_instance_dto
                )
            except ApiException as e:
                logger.error(f'Failed to start process {process_key}:\n{e}')
                raise e
        logger.info(f'Response:\n{response}')

        return response.to_dict()
