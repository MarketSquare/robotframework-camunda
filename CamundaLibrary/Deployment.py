# robot imports
from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger

# python imports
import requests
import os
import json

from generic_camunda_client import ApiException
import generic_camunda_client

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

        with self._shared_resources.api_client as api_client:
            api_instance = generic_camunda_client.DeploymentApi(api_client)
            data = path_bpmn_file
            deployment_name = filename

            try:
                response = api_instance.create_deployment(deploy_changed_only=True,
                                                          enable_duplicate_filtering=True,
                                                          deployment_name=deployment_name,
                                                          data=data)
                logger.info(f'Response from camunda:\t{response}')
            except ApiException as e:
                logger.error(f'Failed to upload {filename}:\n{e}')

        return json.loads(response)

