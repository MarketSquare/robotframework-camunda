from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger
from typing import List, Dict, Any
from camunda.client.external_task_client import ExternalTaskClient
import openapi_client
from openapi_client import ApiException

@library(scope='GLOBAL', version='0.3.4')
class ExternalTask:

    EMPTY_STRING = ""
    KNOWN_TOPICS: Dict[str,Dict[str, Any]] = {}
    CAMUNDA_ENGINE_URL: str = None
    RECENT_PROCESS_INSTANCE: str = EMPTY_STRING

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

    @keyword("Fetch and Lock workloads")
    def fetch_and_lock(self, topic: str) -> Dict:
        """
        Locks and fetches workloads from camunda on a given topic. Returns a list of variable dictionary.
        Each dictionary representing 1 workload.

        If camunda provides a new work item, the work_items process instance id is cached.
        """
        with openapi_client.ApiClient() as api_client:
            # Create an instance of the API class
            api_instance = openapi_client.ExternalTaskApi(api_client)
            fetch_external_tasks_dto = {"topics": [{"topicName": topic}]}

            try:
                api_response = api_instance.fetch_and_lock(fetch_external_tasks_dto=fetch_external_tasks_dto)
                logger.info(api_response)
            except ApiException as e:
                print("Exception when calling ExternalTaskApi->fetch_and_lock: %s\n" % e)

        work_items: List[Dict] = api_response
        if work_items:
            logger.debug(f'Received {len(work_items)} work_items from camunda engine for topic:\t{topic}')
        else:
            logger.debug(f'Received no work items from camunda engine for topic:\t{topic}')

        if not work_items:
            return work_items

        process_instance = work_items[0].get('id')

        if self.RECENT_PROCESS_INSTANCE and self.RECENT_PROCESS_INSTANCE != process_instance:
            logger.warn(f'Fetched from "{process_instance}", but previous instance was not finished:\t'
                        f'{self.RECENT_PROCESS_INSTANCE}')
        self.RECENT_PROCESS_INSTANCE = process_instance

        return [item.get('variables') for item in work_items]

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
        if not process_instance:
            process_instance = self.RECENT_PROCESS_INSTANCE
        external_task = self._get_task_client(topic)
        external_task.complete(process_instance, global_variables=result_set)
        self.RECENT_PROCESS_INSTANCE = self.EMPTY_STRING



    def _create_task_client(self, topic: str) -> ExternalTaskClient:
        if not self.CAMUNDA_ENGINE_URL:
            raise ValueError('No URL to camunda set. Please initialize Library with url or use keyword '
                             '"Set Camunda URL" first.')

        if not topic:
            raise ValueError('No topic set')
        return ExternalTaskClient(topic, self.CAMUNDA_ENGINE_URL)

    def _get_task_client(self, topic, automatically_create_client = False) -> ExternalTaskClient:
        if not topic:
            raise ValueError('Unable to retrieve client, because no topic given.')

        if not self.KNOWN_TOPICS.get(topic, None):
            if not automatically_create_client:
                raise ValueError(f'No client available for topic "{topic}". Either you misspelled the topic or you missed'
                                 f' creating a client before.')

            new_task_client: ExternalTaskClient = self._create_task_client(topic)
            self.KNOWN_TOPICS[topic] = {'client': new_task_client}

        return self.KNOWN_TOPICS[topic]['client']

