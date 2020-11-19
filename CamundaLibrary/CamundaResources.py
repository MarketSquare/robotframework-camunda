class CamundaResources:
    """
    Singleton containing resources shared by Camunda sub libraries
    """
    _instance = None

    _camunda_url: str = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(CamundaResources, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    @property
    def camunda_url(self) -> str:
        return self._camunda_url

    @camunda_url.setter
    def camunda_url(self, value: str):
        self._camunda_url = value

