from generic_camunda_client import Configuration


class CamundaResources:
    """
    Singleton containing resources shared by Camunda sub libraries
    """
    _instance = None

    _client_configuration: Configuration = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(CamundaResources, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

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
