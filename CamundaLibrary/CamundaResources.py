import base64
import json
import os
from collections.abc import Collection
from typing import Dict, Any

from generic_camunda_client import Configuration, ApiClient, VariableValueDto


class CamundaResources:
    """
    Singleton containing resources shared by Camunda sub libraries
    """
    _instance = None

    _client_configuration: Configuration = None

    _api_client: ApiClient = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(CamundaResources, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    # cammunda_url parameter is only required as long not every keyword uses generic-camunda-client
    @property
    def camunda_url(self) -> str:
        return self.client_configuration.host

    @camunda_url.setter
    def camunda_url(self, value: str):
        if not self._client_configuration:
            self.client_configuration = Configuration(host=value)
        else:
            self.client_configuration.host = value

    @property
    def client_configuration(self) -> Configuration:
        return self._client_configuration

    @client_configuration.setter
    def client_configuration(self, value):
        self._client_configuration = value
        if self._api_client:
            self.api_client = self._create_task_client()

    @property
    def api_client(self) -> ApiClient:
        if not self._api_client:
            self._api_client = self._create_task_client()
        return self._api_client

    def _create_task_client(self) -> ApiClient:
        if not self.client_configuration:
            raise ValueError('No URL to camunda set. Please initialize Library with url or use keyword '
                             '"Set Camunda URL" first.')

        # the generated client for camunda ignores auth parameters from the configuration. Therefore we must set default headers here:
        client = ApiClient(self.client_configuration)
        if self.client_configuration.username:
            client.set_default_header('Authorization',self.client_configuration.get_basic_auth_token())
        elif self.client_configuration.api_key:
            identifier = list(self.client_configuration.api_key.keys())[0]
            client.set_default_header('Authorization', self.client_configuration.get_api_key_with_prefix(identifier))

        return client

    @staticmethod
    def convert_openapi_variables_to_dict(open_api_variables: Dict[str, VariableValueDto]) -> Dict:
        """
        Converts the variables to a simple dictionary
        :return: dict
            {"var1": {"value": 1}, "var2": {"value": True}}
            ->
            {"var1": 1, "var2": True}
        """
        if not open_api_variables:
            return {}
        return {k: CamundaResources.convert_variable_dto(v) for k, v in open_api_variables.items()}

    @staticmethod
    def convert_dict_to_openapi_variables(variabes: dict) -> Dict[str, VariableValueDto]:
        """
        Converts the variables to a simple dictionary
        :return: dict
            {"var1": 1, "var2": True}
            ->
            {'var1': {'type': None, 'value': 1, 'value_info': None}, 'var2': {'type': None, 'value': True, 'value_info': None}}

        Example:
        >>> CamundaResources.convert_dict_to_openapi_variables({"var1": 1, "var2": True})
        {'var1': {'type': None, 'value': 1, 'value_info': None}, 'var2': {'type': None, 'value': True, 'value_info': None}}

        >>> CamundaResources.convert_dict_to_openapi_variables({})
        {}
        """
        if not variabes:
            return {}
        return {k: CamundaResources.convert_to_variable_dto(v) for k, v in variabes.items()}

    @staticmethod
    def convert_file_dict_to_openapi_variables(files: Dict[str, str]) -> Dict[str, VariableValueDto]:
        """
        Example:
        >>> CamundaResources.convert_file_dict_to_openapi_variables({'testfile': 'tests/resources/test.txt'})
        {'testfile': {'type': 'File',
         'value': 'VGhpcyBpcyBhIHRlc3QgZmlsZSBmb3IgYSBjYW11bmRhIHByb2Nlc3Mu',
         'value_info': {'filename': 'test.txt', 'mimetype': 'text/plain'}}}

        >>> CamundaResources.convert_file_dict_to_openapi_variables({})
        {}
        """
        if not files:
            return {}
        return {k: CamundaResources.convert_file_to_dto(v) for (k, v) in files.items()}

    @staticmethod
    def convert_file_to_dto(path: str) -> VariableValueDto:
        if not path:
            raise FileNotFoundError('Cannot create DTO from file, because no file provided')

        with open(path, 'r+b') as file:
            file_content = base64.standard_b64encode(file.read()).decode('utf-8')

        base = os.path.basename(path)
        file_name, file_ext = os.path.splitext(base)

        if file_ext.lower() in ['.jpg', '.jpeg', '.jpe']:
            mimetype = 'image/jpeg'
        elif file_ext.lower() in ['.png']:
            mimetype = 'image/png'
        elif file_ext.lower() in ['.pdf']:
            mimetype = 'application/pdf'
        elif file_ext.lower() in ['.txt']:
            mimetype = 'text/plain'
        else:
            mimetype = 'application/octet-stream'
        return VariableValueDto(value=file_content, type='File', value_info={'filename': base, 'mimetype': mimetype})

    @staticmethod
    def convert_to_variable_dto(value: Any) -> VariableValueDto:
        if isinstance(value, str):
            return VariableValueDto(value=value)
        elif isinstance(value, Collection):  # String is also a collection and must be filtered before Collection.
            return VariableValueDto(value=json.dumps(value), type='Json')
        else:
            return VariableValueDto(value=value)

    @staticmethod
    def convert_variable_dto(dto: VariableValueDto) -> Any:
        if dto.type == 'File':
            return dto.to_dict()
        if dto.type == 'Json':
            return json.loads(dto.value)
        return dto.value

    @staticmethod
    def dict_to_camunda_json(d: dict) -> Any:
        """
        Example:
        >>> CamundaResources.dict_to_camunda_json({'a':1})
        {'a': {'value': 1}}

        >>> CamundaResources.dict_to_camunda_json({'person': {'age': 25}})
        {'person': {'value': '{"age": 25}', 'type': 'Json'}}

        >>> CamundaResources.dict_to_camunda_json({'languages': ['English', 'Suomi']})
        {'languages': {'value': '["English", "Suomi"]', 'type': 'Json'}}

        >>> CamundaResources.dict_to_camunda_json({'person': {'age': 25, 'languages': ['English', 'Suomi']}})
        {'person': {'value': '{"age": 25, "languages": ["English", "Suomi"]}', 'type': 'Json'}}
        """
        return {k: {'value': json.dumps(v), 'type': 'Json'} if isinstance(v, Collection) else {'value': v}
                for k, v in d.items()}


if __name__ == '__main__':
    import doctest
    import xmlrunner

    suite = doctest.DocTestSuite()
    xmlrunner.XMLTestRunner(output='logs').run(suite)
