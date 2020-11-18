from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger
from typing import List, Dict, Any
import generic_camunda_client as openapi_client
import time
from generic_camunda_client import ApiException, LockedExternalTaskDto, VariableValueDto


@library(scope='GLOBAL', version='0.3.4')
class ExternalTask:

    WORKER_ID = f'robotframework-camundalibrary-{time.time()}'

    EMPTY_STRING = ""
    KNOWN_TOPICS: Dict[str,Dict[str, Any]] = {}
    CAMUNDA_ENGINE_URL: str = None
    RECENT_PROCESS_INSTANCE: str = EMPTY_STRING
    CAMUNDA_CONFIGURATION: Dict = None
    TASK_ID = ""

    def __init__(self, camunda_engine_url: str = None):
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
        self.CAMUNDA_ENGINE_URL = f'{url}/engine-rest'
        self.CAMUNDA_CONFIGURATION = openapi_client.Configuration(
            host=self.CAMUNDA_ENGINE_URL
        )

    @keyword("Fetch and Lock workloads")
    def fetch_and_lock(self, topic: str) -> Dict:
        """
        Locks and fetches workloads from camunda on a given topic. Returns a list of variable dictionary.
        Each dictionary representing 1 workload.

        If camunda provides a new work item, the work_items process instance id is cached.
        """
        api_response = []
        with self._get_task_client(topic, automatically_create_client=True) as api_client:
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
            return work_items

        self.TASK_ID = work_items[0].id
        self.RECENT_PROCESS_INSTANCE = work_items[0].process_instance_id

        variables: Dict[str, VariableValueDto] = work_items[0].variables
        return {key: value.to_dict() for (key, value) in variables.items()}

    @keyword("Get recent process instance")
    def get_process_instance_id(self):
        """
        Returns cached process instance id from previously called `fetch and lock workloads`
        """
        return self.RECENT_PROCESS_INSTANCE

    @keyword("Complete task")
    def complete(self, topic, process_instance: str = None, result_set: Dict[str, Any] = None):
        """
        Completes a topic for a process instance. If no process isntance id is provided, the most recent cached
        process instance id is used.
        """
        if not topic:
            raise ValueError('Unable complete task, because no topic given')
        with self._get_task_client(topic) as api_client:
            api_instance = openapi_client.ExternalTaskApi(api_client)
            complete_task_dto = openapi_client.CompleteExternalTaskDto(worker_id=self.WORKER_ID, variables=result_set)
            try:
                api_instance.complete_external_task_resource(self.TASK_ID, complete_external_task_dto=complete_task_dto)
                self.RECENT_PROCESS_INSTANCE = self.EMPTY_STRING
                self.TASK_ID=self.EMPTY_STRING
            except ApiException as e:
                logger.error(f"Exception when calling ExternalTaskApi->complete_external_task_resource: {e}\n")

    def _create_task_client(self, topic: str) -> openapi_client.ApiClient:
        if not self.CAMUNDA_ENGINE_URL:
            raise ValueError('No URL to camunda set. Please initialize Library with url or use keyword '
                             '"Set Camunda URL" first.')

        if not topic:
            raise ValueError('No topic set')
        return openapi_client.ApiClient(self.CAMUNDA_CONFIGURATION)

    def _get_task_client(self, topic, automatically_create_client = False) -> openapi_client.ApiClient:
        if not topic:
            raise ValueError('Unable to retrieve client, because no topic given.')

        if not self.KNOWN_TOPICS.get(topic, None):
            if not automatically_create_client:
                raise ValueError(f'No client available for topic "{topic}". Either you misspelled the topic or you missed'
                                 f' creating a client before.')

            new_task_client: openapi_client.ApiClient = self._create_task_client(topic)
            self.KNOWN_TOPICS[topic] = {'client': new_task_client}

        return self.KNOWN_TOPICS[topic]['client']

    @staticmethod
    def convert_openapi_variables_to_dict(open_api_variables: Dict[str, VariableValueDto]) -> Dict:
        """
        Converts the variables to a simple dictionary
        :return: dict
            {"var1": {"value": 1}, "var2": {"value": True}}
            ->
            {"var1": 1, "var2": True}
        """
        result = {}
        for k, v in open_api_variables.items():
            result[k] = v.value
        return result

