# robot imports
from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger

# python imports
import os
from typing import List, Dict, Any
import time

from generic_camunda_client import ApiException, DeploymentWithDefinitionsDto, LockedExternalTaskDto, \
    VariableValueDto, FetchExternalTasksDto, FetchExternalTaskTopicDto, ProcessDefinitionApi, \
    ProcessInstanceWithVariablesDto, StartProcessInstanceDto, ProcessInstanceModificationInstructionDto,\
    ProcessInstanceApi, ProcessInstanceDto
import generic_camunda_client as openapi_client

# local imports
import CamundaResources


@library(scope='GLOBAL')
class CamundaLibrary:

    WORKER_ID = f'robotframework-camundalibrary-{time.time()}'

    EMPTY_STRING = ""
    KNOWN_TOPICS: Dict[str,Dict[str, Any]] = {}
    RECENT_PROCESS_INSTANCE: str = EMPTY_STRING
    TASK_ID = ""

    def __init__(self, camunda_engine_url: str = 'http://localhost:8080'):
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

    @keyword(name='Deploy model from file')
    def deploy_bpmn(self, path_bpmn_file: str):
        """
        Uploads a camunda model to camunda.
        """
        if not path_bpmn_file:
            raise ValueError('Failed deploying model, because no file provided.')

        filename = os.path.basename(path_bpmn_file)

        with self._shared_resources.api_client as api_client:
            api_instance = openapi_client.DeploymentApi(api_client)
            data = path_bpmn_file
            deployment_name = filename

            try:
                response: DeploymentWithDefinitionsDto = api_instance.create_deployment(deploy_changed_only=True,
                                                                                        enable_duplicate_filtering=True,
                                                                                        deployment_name=deployment_name,
                                                                                        data=data)
                logger.info(f'Response from camunda:\t{response}')
            except ApiException as e:
                logger.error(f'Failed to upload {filename}:\n{e}')
                raise e

        return response.to_dict()

    @keyword("Fetch and Lock workloads")
    def fetch_and_lock(self, topic: str) -> Dict:
        """
        Locks and fetches workloads from camunda on a given topic. Returns a list of variable dictionary.
        Each dictionary representing 1 workload.

        If camunda provides a new work item, the work_items process instance id is cached.
        """
        api_response = []
        with self._shared_resources.api_client as api_client:
            # Create an instance of the API class
            api_instance = openapi_client.ExternalTaskApi(api_client)
            topic_dto=FetchExternalTaskTopicDto(topic_name=topic, lock_duration=60000, deserialize_values=True)
            fetch_external_tasks_dto = FetchExternalTasksDto(worker_id=self.WORKER_ID, max_tasks=1, topics=[topic_dto])

            try:
                api_response = api_instance.fetch_and_lock(fetch_external_tasks_dto=fetch_external_tasks_dto)
                logger.info(api_response)
            except ApiException as e:
                logger.error("Exception when calling ExternalTaskApi->fetch_and_lock: %s\n" % e)

        work_items: List[LockedExternalTaskDto] = api_response
        if work_items:
            logger.debug(f'Received {len(work_items)} work_items from camunda engine for topic:\t{topic}')
        else:
            logger.debug(f'Received no work items from camunda engine for topic:\t{topic}')

        if not work_items:
            return {}

        self.TASK_ID = work_items[0].id
        self.RECENT_PROCESS_INSTANCE = work_items[0].process_instance_id

        variables: Dict[str, VariableValueDto] = work_items[0].variables
        return CamundaResources.convert_openapi_variables_to_dict(variables)

    @keyword("Get recent process instance")
    def get_process_instance_id(self):
        """
        Returns cached process instance id from previously called `fetch and lock workloads`
        """
        return self.RECENT_PROCESS_INSTANCE

    @keyword("Complete task")
    def complete(self, result_set: Dict[str, Any] = None, files: Dict = None):
        """
        Completes recent task.

        result_set must be a dictionary like: {'key' : 'value'}
        """
        if not self.TASK_ID:
            logger.warn('No task to complete. Maybe you did not fetch and lock a workitem before?')
        else:
            with self._shared_resources.api_client as api_client:
                api_instance = openapi_client.ExternalTaskApi(api_client)
                variables = CamundaResources.convert_dict_to_openapi_variables(result_set)
                openapi_files = CamundaResources.convert_file_dict_to_openapi_variables(files)
                variables.update(openapi_files)
                complete_task_dto = openapi_client.CompleteExternalTaskDto(worker_id=self.WORKER_ID, variables=variables)
                try:
                    logger.debug(f"Sending to Camunda for completing Task:\n{complete_task_dto}")
                    api_instance.complete_external_task_resource(self.TASK_ID, complete_external_task_dto=complete_task_dto)
                    self.RECENT_PROCESS_INSTANCE = self.EMPTY_STRING
                    self.TASK_ID=self.EMPTY_STRING
                except ApiException as e:
                    logger.error(f"Exception when calling ExternalTaskApi->complete_external_task_resource: {e}\n")

    @keyword("Download file from variable")
    def download_file_from_variable(self, variable_name: str) -> str:
        if not self.RECENT_PROCESS_INSTANCE:
            logger.warn('Could not download file for variable. Maybe you did not fetch and lock a workitem before?')
        else:
            with self._shared_resources.api_client as api_client:
                api_instance = openapi_client.ProcessInstanceApi(api_client)

                try:
                    response = api_instance.get_process_instance_variable_binary(id=self.RECENT_PROCESS_INSTANCE, var_name=variable_name)
                    logger.debug(response)
                except ApiException as e:
                    logger.error(f"Exception when calling ExternalTaskApi->get_process_instance_variable_binary: {e}\n")
                return response


    @keyword("Unlock")
    def unlock(self):
        """
        Unlocks recent task.
        """
        if not self.TASK_ID:
            logger.warn('No task to unlock. Maybe you did not fetch and lock a workitem before?')
        else:
            with self._shared_resources.api_client as api_client:
                api_instance = openapi_client.ExternalTaskApi(api_client)
                try:
                    api_instance.unlock(self.TASK_ID)
                    self.RECENT_PROCESS_INSTANCE = self.EMPTY_STRING
                    self.TASK_ID=self.EMPTY_STRING
                except ApiException as e:
                    logger.error(f"Exception when calling ExternalTaskApi->unlock: {e}\n")

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
            api_instance: ProcessDefinitionApi = openapi_client.ProcessDefinitionApi(api_client)
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

    @keyword("Delete process instance")
    def delete_process_instance(self, process_instance_id):
        """
        USE WITH CARE: Deletes a process instance by id. All data in this process instance will be lost.
        """
        with self._shared_resources.api_client as api_client:
            api_instance = openapi_client.ProcessInstanceApi(api_client)

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
            api_instance: ProcessInstanceApi = openapi_client.ProcessInstanceApi(api_client)

            try:
                response: List[ProcessInstanceDto] = api_instance.get_process_instances(
                    process_definition_key=process_definition_key,
                    active='true'
                )
            except ApiException as e:
                logger.error(f'Failed to get process instances of process {process_definition_key}:\n{e}')
                raise e

        return [process_instance.to_dict() for process_instance in response]
