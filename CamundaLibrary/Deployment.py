# robot imports
from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger

# python imports
import requests
import os
import json

# local imports
from CamundaLibrary.CamundaResources import CamundaResources


@library(scope='GLOBAL', version='0.3.4')
class Deployment:

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

    @keyword(name='Deploy model from file')
    def deploy_bpmn(self, path_bpmn_file: str):
        """
        Uploads a camunda model to camunda.
        """
        if not path_bpmn_file:
            raise ValueError('Failed deploying model, because no file provided.')

        filename = os.path.basename(path_bpmn_file)

        camunda_deployment_info_part = {
            'deployment-name': filename,
        }
        model_part = {'data': (os.path.basename(path_bpmn_file), open(path_bpmn_file, 'r'))}
        response = requests.post(f'{self._shared_resources.camunda_url}/deployment/create', data=camunda_deployment_info_part, files=model_part)
        logger.info(f'Response from camunda:\t{response.status_code}')
        response.raise_for_status()

        return json.loads(response.content)

