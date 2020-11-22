from generic_camunda_client import Configuration, ApiClient


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
            self._get_task_client()

    @property
    def api_client(self) -> ApiClient:
        return self._get_task_client()

    def _create_task_client(self) -> ApiClient:
        if not self._shared_resources.camunda_url:
            raise ValueError('No URL to camunda set. Please initialize Library with url or use keyword '
                             '"Set Camunda URL" first.')

        return ApiClient(self._shared_resources.client_configuration)

    def _get_task_client(self) -> ApiClient:
        if not self._api_client:

            self._api_client = self._create_task_client()

        return self._api_client

