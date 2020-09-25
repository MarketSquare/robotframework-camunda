from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger
from typing import Dict, Any
from camunda.client.external_task_client import ExternalTaskClient


@library(scope='GLOBAL', version='0.0.1')
class ExternalTask:

    KNOWN_TOPICS: Dict[str,Dict[str, Any]] = {}
    CAMUNDA_ENGINE_URL: str = None

    def __init__(self, camunda_engine_url: str = None):
        if camunda_engine_url:
            self.CAMUNDA_ENGINE_URL = camunda_engine_url

    @keyword("Fetch and Lock")
    def fetch_and_lock(self, topic: str):
        external_task: ExternalTask = self._get_task_client(topic)
        work_items = external_task.fetch_and_lock([topic])
        if work_items:
            logger.debug(f'Recived {len(work_items)} work_items from camunda engine for topic:\t{topic}')
        else:
            logger.debug(f'Received no work items from camunda engine for topic:\t{topic}')

        return work_items

    @keyword("Set Camunda URL")
    def set_camunda_url(self, url: str):
        if not url:
            raise ValueError('Cannot set camunda engine url: no url given.')
        self.CAMUNDA_ENGINE_URL = url

    def _create_task_client(self, topic: str) -> ExternalTaskClient:
        if not self.CAMUNDA_ENGINE_URL:
            raise ValueError('No URL to camunda set. Please initialize Library with url or use keyword '
                             '"Set Camunda URL" first.')

        if not topic:
            raise ValueError('No topic set')
        return ExternalTaskClient(topic, self.CAMUNDA_ENGINE_URL)

    def _get_task_client(self, topic) -> ExternalTaskClient:
        if not self.KNOWN_TOPICS.get(topic, None):
            new_task_client: ExternalTask = self._create_task_client(topic)
            self.KNOWN_TOPICS[topic] = {'client': new_task_client}

        return self.KNOWN_TOPICS[topic]['client']

