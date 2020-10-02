from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger
import requests
import os
import json


@library(scope='GLOBAL')
class Deployment:

    CAMUNDA_HOST = None

    def __init__(self, camunda_host: str = ''):
        self.CAMUNDA_HOST = camunda_host

    @keyword("Set Camunda URL")
    def set_camunda_url(self, url: str):
        """
        Sets url for camunda eninge. Only necessary when URL cannot be set during initialization of this library or
        you want to switch camunda url for some reason.
        """
        if not url:
            raise ValueError('Cannot set camunda engine url: no url given.')
        self.CAMUNDA_HOST = url

    @keyword(name='Deploy model from file')
    def deploy_bpmn(self, bpmn_file: str):
        if not bpmn_file:
            raise ValueError('Failed deploying model, because no file provided.')

        filename = os.path.basename(bpmn_file)

        camunda_deployment_info_part = {
            'deployment-name': filename,
        }
        model_part = {'data': (os.path.basename(bpmn_file), open(bpmn_file, 'r'))}
        response = requests.post(f'{self.CAMUNDA_HOST}/engine-rest/deployment/create', data=camunda_deployment_info_part, files=model_part)
        logger.info(f'Response from camunda:\t{response.status_code}')
        response.raise_for_status()

        return json.loads(response.content)

