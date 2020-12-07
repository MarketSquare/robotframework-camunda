from generic_camunda_client import Configuration, ApiClient, VariableValueDto
from typing import Dict


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
            self.api_client

    @property
    def api_client(self) -> ApiClient:
        if not self._api_client:
            self._api_client = self._create_task_client()
        return self._api_client

    def _create_task_client(self) -> ApiClient:
        if not self.client_configuration:
            raise ValueError('No URL to camunda set. Please initialize Library with url or use keyword '
                             '"Set Camunda URL" first.')

        return ApiClient(self.client_configuration)

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
        if open_api_variables:
            for k, v in open_api_variables.items():
                result[k] = v.value
        return result

    @staticmethod
    def convert_dict_to_openapi_variables(variabes: dict) -> Dict[str,VariableValueDto]:
        """
        Converts the variables to a simple dictionary
        :return: dict
            {"var1": 1, "var2": True}
            ->
            {"var1": {"value": "1", "type": "String"}, "var2": {"value": "True", "type": "String"}}
        """
        result: Dict[str, VariableValueDto] = {}
        if variabes:
            for k,v in variabes.items():
                result[k] = VariableValueDto(value=v, type="String")
        return result


