from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger
from typing import List, Dict, Any
from camunda.client.external_task_client import ExternalTaskClient


@library(scope='GLOBAL')
class ExternalTask:

    EMPTY_STRING = ""
    KNOWN_TOPICS: Dict[str,Dict[str, Any]] = {}
    CAMUNDA_ENGINE_URL: str = None
    RECENT_TASK_ID: str = EMPTY_STRING

    def __init__(self, camunda_engine_url: str = None):
        if camunda_engine_url:
            self.CAMUNDA_ENGINE_URL = camunda_engine_url

    @keyword("Set Camunda URL")
    def set_camunda_url(self, url: str):
        """
        Sets url for camunda eninge. Only necessary when URL cannot be set during initialization of this library or
        you want to switch camunda url for some reason.
        """
        if not url:
            raise ValueError('Cannot set camunda engine url: no url given.')
        self.CAMUNDA_ENGINE_URL = url

    @keyword("Fetch and Lock workloads")
    def fetch_and_lock(self, topic: str) -> Dict:
        """
        Locks and fetches workloads from camunda on a given topic. Returns a list of varaible dictionary.
        Each dictionary representing 1 workload.
        """
        external_task: ExternalTask = self._get_task_client(topic, automatically_create_client=True)
        work_items: List[Dict] = external_task.fetch_and_lock([topic])
        if work_items:
            logger.debug(f'Recived {len(work_items)} work_items from camunda engine for topic:\t{topic}')
        else:
            logger.debug(f'Received no work items from camunda engine for topic:\t{topic}')

        if not work_items:
            external_task_id = self.EMPTY_STRING
        else:
            external_task_id = work_items[0].get('id')

        if self.RECENT_TASK_ID and self.RECENT_TASK_ID != external_task_id:
            logger.warn(f'Fetched from "{external_task_id}" which is different task than before:\t{self.RECENT_TASK_ID}')
        self.RECENT_TASK_ID = external_task_id

        if not work_items:
            return work_items
        else:
            return [item.get('variables') for item in work_items]

    @keyword("Get recent task id")
    def get_recent_task_id(self):
        return self.RECENT_TASK_ID

    @keyword("Complete task")
    def complete(self, topic, task_id: str = None, result_set: Dict[str, Any] = None):
        if not topic:
            raise ValueError('Unable complete task, because no topic given')
        if not task_id:
            task_id = self.RECENT_TASK_ID
        external_task = self._create_task_client(topic)
        external_task.complete(task_id, global_variables=result_set)



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

            new_task_client: ExternalTask = self._create_task_client(topic)
            self.KNOWN_TOPICS[topic] = {'client': new_task_client}

        return self.KNOWN_TOPICS[topic]['client']

