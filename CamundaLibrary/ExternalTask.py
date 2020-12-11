# robot imports
from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger

# general python import
from typing import List, Dict, Any
import time

# camunda client imports
import generic_camunda_client as openapi_client
from generic_camunda_client import ApiException, LockedExternalTaskDto, VariableValueDto

# local imports
from CamundaLibrary.CamundaResources import CamundaResources


@library(scope='GLOBAL')
class ExternalTask:

    WORKER_ID = f'robotframework-camundalibrary-{time.time()}'

    EMPTY_STRING = ""
    KNOWN_TOPICS: Dict[str,Dict[str, Any]] = {}
    RECENT_PROCESS_INSTANCE: str = EMPTY_STRING
    TASK_ID = ""

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
            fetch_external_tasks_dto = {
                "workerId": self.WORKER_ID,
                "maxTasks": 1,
                "topics": [
                    {
                        "topicName": topic,
                        "lockDuration": 600000,
                    }
                ]
            }

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
    def complete(self, result_set: Dict[str, Any] = None):
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
                complete_task_dto = openapi_client.CompleteExternalTaskDto(worker_id=self.WORKER_ID, variables=variables)
                try:
                    logger.debug(f"Sending to Camunda for completing Task:\n{complete_task_dto}")
                    api_instance.complete_external_task_resource(self.TASK_ID, complete_external_task_dto=complete_task_dto)
                    self.RECENT_PROCESS_INSTANCE = self.EMPTY_STRING
                    self.TASK_ID=self.EMPTY_STRING
                except ApiException as e:
                    logger.error(f"Exception when calling ExternalTaskApi->complete_external_task_resource: {e}\n")

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