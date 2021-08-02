# robot imports

from robot.api.deco import library, keyword
from robot.api.logger import librarylogger as logger

# requests import
from requests import HTTPError
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from url_normalize import url_normalize

# python imports
import os
from typing import List, Dict, Any
import time

from generic_camunda_client import ApiException, CountResultDto, DeploymentWithDefinitionsDto, DeploymentDto, \
    LockedExternalTaskDto, \
    VariableValueDto, FetchExternalTasksDto, FetchExternalTaskTopicDto, ProcessDefinitionApi, \
    ProcessInstanceWithVariablesDto, StartProcessInstanceDto, ProcessInstanceModificationInstructionDto, \
    ProcessInstanceApi, ProcessInstanceDto, VersionApi, EvaluateDecisionDto, MessageApi, \
    MessageCorrelationResultWithVariableDto, CorrelationMessageDto
import generic_camunda_client as openapi_client

# local imports
from .CamundaResources import CamundaResources


@library(scope='GLOBAL')
class CamundaLibrary:
    """
    Library for Camunda integration in Robot Framework

    = Installation =

    == Camunda ==

    Easiest to run Camunda in docker:
    | docker run -d --name camunda -p 8080:8080 camunda/camunda-bpm-platform:run-latest

    == CamundaLibrary ==
    You can use pip for installing CamundaLibrary:
    | pip install robotframework-camunda

    = Usage =

    The library provides convenience keywords for accessing Camunda via REST API. You may deploy models,
    start processes, fetch workloads and complete them.

    When initializing the library the default url for Camunda is `http://localhost:8080` which is the default when
    running Camunda locally. It is best practice to provide a variable for the url, so it can be set dynamically
    by the executing environment (like on local machine, in pipeline, on test system and production):

    | Library | CamundaLibrary | ${CAMUNDA_URL} |

    Running locally:
    | robot -v "CAMUNDA_URL:http://localhost:8080" task.robot

    Running in production
    | robot -v "CAMUNDA_URL:https://camunda-prod.mycompany.io" task.robot

    = Execution =

    In contrast to external workers that are common for Camunda, tasks implemented with CamundaLibrary do not
    _subscribe_ on certain topics. A robot tasks is supposed to run once. How frequent the task is executed is up
    to the operating environment of the developer.

    == Subscribing a topic / long polling ==
    You may achieve a kind of subscription by providing the ``asyncResponseTimeout`` with the `Fetch workload`
    keyword in order to achieve [https://docs.camunda.org/manual/7.14/user-guide/process-engine/external-tasks/#long-polling-to-fetch-and-lock-external-tasks|Long Polling].

    | ${variables} | fetch workload | my_topic | async_response_timeout=60000 |
    | log | Waited at most 1 minute before this log statement got executed |

    = Missing Keywords =

    If you miss a keyword, you can utilize the REST API from Camunda by yourself using the [https://github.com/MarketSquare/robotframework-requests|RequestsLibrary].
    With RequestsLibrary you can access all of the fully documented [https://docs.camunda.org/manual/latest/reference/rest/|Camunda REST API].

    = Feedback =

    Feedback is very much appreciated regardless if it is comments, reported issues, feature requests or even merge
    requests. You are welcome to participating in any way at the [https://gitlab.com/postadress/robotframework/robotframework-camunda|GitLab project of CamundaLibrary].
    """

    WORKER_ID = f'robotframework-camundalibrary-{time.time()}'

    EMPTY_STRING = ""
    KNOWN_TOPICS: Dict[str,Dict[str, Any]] = {}
    FETCH_RESPONSE: LockedExternalTaskDto = None

    def __init__(self, camunda_engine_url: str = 'http://localhost:8080'):
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
        self._shared_resources.camunda_url = url_normalize(f'{url}/engine-rest')

    @keyword("Get Camunda URL")
    def get_camunda_url(self) -> str:
        return self._shared_resources.camunda_url

    @keyword("Get amount of workloads")
    def get_amount_of_workloads(self, topic: str, **kwargs) -> int:
        """
        Retrieves count of tasks. By default expects a topic name, but all parameters from the original endpoint
        may be provided: https://docs.camunda.org/manual/latest/reference/rest/external-task/get-query-count/
        """
        with self._shared_resources.api_client as api_client:
            api_instance = openapi_client.ExternalTaskApi(api_client)

            try:
                response: CountResultDto = api_instance.get_external_tasks_count(topic_name=topic, **kwargs)
            except ApiException as e:
                logger.error(f'Failed to count workload for topic "{topic}":\n{e}')
                raise e

        logger.info(f'Amount of workloads for "{topic}":\t{response.count}')
        return response.count

    @keyword(name='Deploy Model From File', tags=['deployment'])
    def deploy_model_from_file(self, path_to_model):
        """*DEPRECATED*

        Use `Deploy`
        """
        logger.warn('Keyword "Deploy Model From File" is deprecated. Use "Deploy" instead.')
        return self.deploy(path_to_model)

    @keyword(name='Deploy', tags=['deployment'])
    def deploy(self, *args):
        """Creates a deployment from all given files and uploads them to camunda.

        Return response from camunda rest api as dictionary.
        Further documentation: https://docs.camunda.org/manual/7.14/reference/rest/deployment/post-deployment/

        By default, this keyword only deploys changed models and filters duplicates. Deployment name is the filename of
        the first file.

        Example:
            | ${response} | *Deploy model from file* | _../bpmn/my_model.bpnm_ | _../forms/my_forms.html_ |
        """
        if not args:
            raise ValueError('Failed deploying model, because no file provided.')

        if len(args) > 1:
            # We have to use plain REST then when uploading more than 1 file.
            return self.deploy_multiple_files(*args)

        filename = os.path.basename(args[0])

        with self._shared_resources.api_client as api_client:
            api_instance = openapi_client.DeploymentApi(api_client)
            data = [*args]
            deployment_name = filename

            try:
                response: DeploymentWithDefinitionsDto = api_instance.create_deployment(deploy_changed_only=True,
                                                                                        enable_duplicate_filtering=True,
                                                                                        deployment_name=deployment_name,
                                                                                        data=data)
                logger.info(f'Response from camunda:\t{response}')
            except ApiException as e:
                logger.error(f'Failed to upload {filename}:\n{e}')
                raise e

        return response.to_dict()

    def deploy_multiple_files(self, *args):
        """
        # Due to https://jira.camunda.com/browse/CAM-13105 we cannot use generic camunda client when dealing with
        # multiple files. We have to use plain REST then.
        """

        fields = {
            'deployment-name': f'{os.path.basename(args[0])}',
        }

        for file in args:
            filename = os.path.basename(file)
            fields[f'{filename}'] = (filename, open(file, 'rb'), 'application/octet-stream')

        multipart_data = MultipartEncoder(
            fields=fields
        )

        logger.debug(multipart_data.fields)

        response = requests.post(f'{self._shared_resources.camunda_url}/deployment/create', data=multipart_data,
                                 headers={'Content-Type': multipart_data.content_type})
        json = response.json()
        try:
            response.raise_for_status()
            logger.debug(json)
        except HTTPError as e:
            logger.error(json)
            raise e

        return json

    @keyword(name='Get deployments', tags=['deployment'])
    def get_deployments(self, deployment_id: str = None, **kwargs):
        """
        Retrieves all deployments that match given criteria. All parameters are available from https://docs.camunda.org/manual/latest/reference/rest/deployment/get-query/

        Example:
            | ${list_of_deployments} | get deployments | ${my_deployments_id} |
            | ${list_of_deployments} | get deployments | id=${my_deployments_id} |
            | ${list_of_deployments} | get deployments | after=2013-01-23T14:42:45.000+0200 |
        """
        if deployment_id:
            kwargs['id'] = deployment_id

        with self._shared_resources.api_client as api_client:
            api_instance = openapi_client.DeploymentApi(api_client)

            try:
                response: List[DeploymentDto] = api_instance.get_deployments(**kwargs)
                logger.info(f'Response from camunda:\t{response}')
            except ApiException as e:
                logger.error(f'Failed get deployments:\n{e}')
                raise e

        return [r.to_dict() for r in response]

    @keyword("Deliver Message", tags="message")
    def deliver_message(self, message_name, **kwargs):
        """
        Delivers a message using Camunda REST API: https://docs.camunda.org/manual/7.15/reference/rest/message/post-message/

        Example:
            | ${result} | deliver message | msg_payment_received |
            | ${result} | deliver message | msg_payment_received | process_variables = ${variable_dictionary} |
            | ${result} | deliver message | msg_payment_received | business_key = ${correlating_business_key} |
        """
        with self._shared_resources.api_client as api_client:
            api_instance: MessageApi = openapi_client.MessageApi(api_client)
            correlation_message: CorrelationMessageDto = CorrelationMessageDto(**kwargs)
            correlation_message.message_name = message_name

            try:
                response: MessageCorrelationResultWithVariableDto = api_instance.deliver_message(correlation_message)
            except ApiException as e:
                logger.error(f'Failed to deliver message:\n{e}')
                raise e
        return response.to_dict()

    @keyword("Fetch and Lock workloads", tags=['task', 'deprecated'])
    def fetch_and_lock_workloads(self, topic, **kwargs) -> Dict:
        """*DEPRECATED*

        Use `fetch workload`
        """
        logger.warn('Keyword "Fetch and Lock workloads" is deprecated. Use "Fetch workload" instead.')
        return self.fetch_workload(topic, **kwargs)

    @keyword("Fetch Workload", tags=['task'])
    def fetch_workload(self, topic: str, async_response_timeout=None, use_priority=None, **kwargs) -> Dict:
        """
        Locks and fetches workloads from camunda on a given topic. Returns a list of variable dictionary.
        Each dictionary representing 1 workload from a process instance.

        If a process instance was fetched, the process instance is cached and can be retrieved by keyword
        `Get recent process instance`

        The only mandatory parameter for this keyword is *topic* which is the name of the topic to fetch workload from.
        More parameters can be added from the Camunda documentation: https://docs.camunda.org/manual/7.14/reference/rest/external-task/fetch/

        If not provided, this keyword will use a lock_duration of 60000 ms (10 minutes) and set {{deserialize_value=True}}

        Examples:
            | ${input_variables} | *Create Dictionary* | _name=Robot_ |
            | | *start process* | _my_demo_ | _${input_variables}_ |
            | ${variables} | *fetch and lock workloads* | _first_task_in_demo_ |
            | | *Dictionary Should Contain Key* | _${variables}_ | _name_ |
            | | *Should Be Equal As String* | _Robot_ | _${variables}[name]_ |

        Example deserializing only some variables:
            | ${input_variables} | *Create Dictionary* | _name=Robot_ | _profession=Framework_ |
            | | *start process* | _my_demo_ | _${input_variables}_ |
            | ${variables_of_interest} | *Create List* | _profession_ |
            | ${variables} | *Fetch Workload* | _first_task_in_demo_ | _variables=${variables_of_interest}_ |
            | | *Dictionary Should Not Contain Key* | _${variables}_ | _name_ |
            | | *Dictionary Should Contain Key* | _${variables}_ | _profession_ |
            | | *Should Be Equal As String* | _Framework_ | _${variables}[profession]_ |
        """
        api_response = []
        with self._shared_resources.api_client as api_client:
            # Create an instance of the API class
            api_instance = openapi_client.ExternalTaskApi(api_client)
            if 'lock_duration' not in kwargs:
                kwargs['lock_duration'] = 60000
            if 'deserialize_values' not in kwargs:
                kwargs['deserialize_values'] = False
            topic_dto=FetchExternalTaskTopicDto(topic_name=topic, **kwargs)
            fetch_external_tasks_dto = FetchExternalTasksDto(worker_id=self.WORKER_ID, max_tasks=1,
                                                             async_response_timeout=async_response_timeout,
                                                             use_priority=use_priority,
                                                             topics=[topic_dto])

            try:
                api_response = api_instance.fetch_and_lock(fetch_external_tasks_dto=fetch_external_tasks_dto)
                logger.info(api_response)
            except ApiException as e:
                logger.error("Exception when calling ExternalTaskApi->fetch_and_lock: %s\n" % e)

        work_items: List[LockedExternalTaskDto] = api_response
        if work_items:
            logger.debug(f'Received {len(work_items)} work_items from camunda engine for topic:\t{topic}')
        else:
            logger.debug(f'Received no work items from camunda engine for topic:\t{topic}')

        if not work_items:
            return {}

        self.FETCH_RESPONSE = work_items[0]

        variables: Dict[str, VariableValueDto] = self.FETCH_RESPONSE.variables
        return CamundaResources.convert_openapi_variables_to_dict(variables)

    @keyword("Get recent process instance", tags=['task', 'deprecated'])
    def get_process_instance_id(self):
        """*DEPRECATED*
        _Use `get fetch response` instead and check for ``process_instance_id`` element on the fetch reponse:
        ``fetch_response[process_instance]``_

        Returns cached process instance id from previously called `fetch and lock workloads`.

        *Only this keyword can certainly tell, if workload has been fetched from Camunda*

        Example:
            | ${variables} | fetch and lock workloads | my_first_task_in_demo | |
            | Run keyword if | not ${variables} | log | No variables found, but is due to lack of variables or because no workload was available? Must check process instance |
            | ${process_instance} | get recent process instance | | |
            | Run keyword if | ${process_instance} | complete task | |
        """
        logger.warn('Method is deprecated. Use "Get fetch response"')
        if self.FETCH_RESPONSE:
            return self.FETCH_RESPONSE.process_instance_id
        return self.EMPTY_STRING

    @keyword("Get fetch response", tags=['task'])
    def get_fetch_response(self):
        """Returns cached response from the last call of `fetch workload`.

        The response contains all kind of data that is required for custom REST Calls.

        Example:
            | *** Settings *** |
            | *Library* | RequestsLibrary |
            | |
            | *** Tasks *** |
            | | *Create Session* | _alias=camunda_ | _url=http://localhost:8080_ |
            | | ${variables} | *fetch and lock workloads* | _my_first_task_in_demo_ | |
            | | ${fetch_response} | *get fetch response* | | |
            | | *POST On Session* | _camunda_ | _engine-rest/external-task/${fetch_response}[id]/complete_ | _json=${{ {'workerId': '${fetch_response}[worker_id]'} }}_ |
        """
        if self.FETCH_RESPONSE:
            return self.FETCH_RESPONSE.to_dict()
        return self.FETCH_RESPONSE

    @keyword("Drop fetch response")
    def drop_fetch_response(self):
        self.FETCH_RESPONSE = {}

    @keyword("Complete task", tags=['task'])
    def complete(self, result_set: Dict[str, Any] = None, files: Dict = None):
        """
        Completes the task that was fetched before with `fetch workload`.

        *Requires `fetch workload` to run before this one, logs warning instead.*

        Additonal variables can be provided as dictionary in _result_set_ .
        Files can be provided as dictionary of filename and patch.

        Examples:

            | _# fetch and immediately complete_ |
            | | *fetch workload* | _my_topic_ |
            | | *complete task* | |
            | |
            | _# fetch and complete with return values_ |
            | | *fetch workload* | _decide_on_dish_ |
            | ${new_variables} | *Create Dictionary* | _my_dish=salad_ |
            | | *complete task* | _result_set=${new_variables}_ |
            | |
            | _# fetch and complete with return values and files_ |
            | | *fetch workload* | _decide_on_haircut_ |
            | ${return_values} | *Create Dictionary* | _style=short hair_ |
            | ${files} | *Create Dictionary* | _should_look_like=~/favorites/beckham.jpg_ |
            | | *complete task* | _${return_values}_ | _${files}_ |
        """
        if not self.FETCH_RESPONSE:
            logger.warn('No task to complete. Maybe you did not fetch and lock a workitem before?')
        else:
            with self._shared_resources.api_client as api_client:
                api_instance = openapi_client.ExternalTaskApi(api_client)
                variables = CamundaResources.convert_dict_to_openapi_variables(result_set)
                openapi_files = CamundaResources.convert_file_dict_to_openapi_variables(files)
                variables.update(openapi_files)
                complete_task_dto = openapi_client.CompleteExternalTaskDto(worker_id=self.WORKER_ID, variables=variables)
                try:
                    logger.debug(f"Sending to Camunda for completing Task:\n{complete_task_dto}")
                    api_instance.complete_external_task_resource(self.FETCH_RESPONSE.id, complete_external_task_dto=complete_task_dto)
                    self.drop_fetch_response()
                except ApiException as e:
                    logger.error(f"Exception when calling ExternalTaskApi->complete_external_task_resource: {e}\n")

    @keyword("Download file from variable", tags=['task'])
    def download_file_from_variable(self, variable_name: str) -> str:
        if not self.FETCH_RESPONSE:
            logger.warn('Could not download file for variable. Maybe you did not fetch and lock a workitem before?')
        else:
            with self._shared_resources.api_client as api_client:
                api_instance = openapi_client.ProcessInstanceApi(api_client)

                try:
                    response = api_instance.get_process_instance_variable_binary(
                        id=self.FETCH_RESPONSE.process_instance_id, var_name=variable_name)
                    logger.debug(response)
                except ApiException as e:
                    logger.error(f"Exception when calling ExternalTaskApi->get_process_instance_variable_binary: {e}\n")
                return response

    @keyword("Unlock", tags=['task'])
    def unlock(self):
        """
        Unlocks recent task.
        """
        if not self.FETCH_RESPONSE:
            logger.warn('No task to unlock. Maybe you did not fetch and lock a workitem before?')
        else:
            with self._shared_resources.api_client as api_client:
                api_instance = openapi_client.ExternalTaskApi(api_client)
                try:
                    api_instance.unlock(self.FETCH_RESPONSE.id)
                    self.drop_fetch_response()
                except ApiException as e:
                    logger.error(f"Exception when calling ExternalTaskApi->unlock: {e}\n")

    @keyword("Start process", tags=['process'])
    def start_process(self, process_key: str, variables: Dict = None, files: Dict = None,
                      before_activity_id: str = None, after_activity_id: str = None,**kwargs) -> Dict:
        """
        Starts a new process instance from a process definition with given key.

        variables: _optional_ dictionary like: {'variable name' : 'value'}

        files: _optional_ dictionary like: {'variable name' : path}. will be attached to variables in Camunda

        before_activity_id: _optional_ id of activity at which the process starts before. *CANNOT BE USED TOGETHER WITH _after_activity_id_*

        after_activity_id: _optional_ id of activity at which the process starts after. *CANNOT BE USED TOGETHER WITH _before_activity_id_*

        Returns response from Camunda as dictionary

        == Examples ==
        | `start process`      | apply for job promotion    | _variables_= { 'employee' : 'John Doe', 'permission_for_application_granted' : True}   | _files_ = { 'cv' : 'documents/my_life.md'}  | _after_activity_id_ = 'Activity_ask_boss_for_persmission'   |
        | `start process` | apply for promotion | business_key=John again |
        """
        if not process_key:
            raise ValueError('Error starting process. No process key provided.')

        if before_activity_id and after_activity_id:
            raise AssertionError('2 activity ids provided. Cannot start before and after an activity.')

        with self._shared_resources.api_client as api_client:
            api_instance: ProcessDefinitionApi = openapi_client.ProcessDefinitionApi(api_client)
            openapi_variables = CamundaResources.convert_dict_to_openapi_variables(variables)
            openapi_files = CamundaResources.convert_file_dict_to_openapi_variables(files)
            openapi_variables.update(openapi_files)

            if before_activity_id or after_activity_id:
                instruction: ProcessInstanceModificationInstructionDto = ProcessInstanceModificationInstructionDto(
                    type='startBeforeActivity' if before_activity_id else 'startAfterActivity',
                    activity_id=before_activity_id if before_activity_id else after_activity_id,
                )
                kwargs.update(start_instructions=[instruction])

            start_process_instance_dto: StartProcessInstanceDto = StartProcessInstanceDto(
                variables=openapi_variables,
                **kwargs
            )

            try:
                response: ProcessInstanceWithVariablesDto = api_instance.start_process_instance_by_key(
                    key=process_key,
                    start_process_instance_dto=start_process_instance_dto
                )
            except ApiException as e:
                logger.error(f'Failed to start process {process_key}:\n{e}')
                raise e
        logger.info(f'Response:\n{response}')

        return response.to_dict()

    @keyword("Delete process instance", tags=['process'])
    def delete_process_instance(self, process_instance_id):
        """
        USE WITH CARE: Deletes a process instance by id. All data in this process instance will be lost.
        """
        with self._shared_resources.api_client as api_client:
            api_instance = openapi_client.ProcessInstanceApi(api_client)

            try:
                api_instance.delete_process_instance(id=process_instance_id)
            except ApiException as e:
                logger.error(f'Failed to delete process instance {process_instance_id}:\n{e}')
                raise e

    @keyword("Get all active process instances", tags=['process'])
    def get_all_process_instances(self, process_definition_key):
        """
        Returns a list of process instances that are active for a certain process definition identified by key.
        """
        with self._shared_resources.api_client as api_client:
            api_instance: ProcessInstanceApi = openapi_client.ProcessInstanceApi(api_client)

            try:
                response: List[ProcessInstanceDto] = api_instance.get_process_instances(
                    process_definition_key=process_definition_key,
                    active='true'
                )
            except ApiException as e:
                logger.error(f'Failed to get process instances of process {process_definition_key}:\n{e}')
                raise e

        return [process_instance.to_dict() for process_instance in response]

    @keyword("Get Version", tags=['version'])
    def get_version(self):
        """
        Returns Version of Camunda.

        == Example ==
        | ${camunda_version_dto} | Get Version |
        | ${camunda_version} | Set Variable | ${camunda_version_dto.version} |
        """
        with self._shared_resources.api_client as api_client:
            api_instance: VersionApi = openapi_client.VersionApi(api_client)
            return api_instance.get_rest_api_version()

    @keyword("Get Process Definitions", tags=['process'])
    def get_process_definitions(self, **kwargs):
        """
        Returns a list of process definitions that fulfill given parameters.

        See Rest API documentation on ``https://docs.camunda.org/manual`` for available parameters.

        == Example ==
        | ${list} | Get Process Definitions | name=my_process_definition |
        """
        with self._shared_resources.api_client as api_client:
            api_instance: ProcessDefinitionApi = openapi_client.ProcessDefinitionApi(api_client)

            try:
                response = api_instance.get_process_definitions(**kwargs)
            except ApiException as e:
                logger.error(f'Failed to get process definitions:\n{e}')
                raise e
        return response

    @keyword("Get Activity Instance", tags=['process'])
    def get_activity_instance(self, **kwargs):
        """
        Returns an Activity Instance (Tree) for a given process instance.

        == Example ==
        | ${tree} | Get Activity Instance | id=fcab43bc-b970-11eb-be75-0242ac110002 |

        https://docs.camunda.org/manual/7.5/reference/rest/process-instance/get-activity-instances/
        """
        with self._shared_resources.api_client as api_client:
            api_instance: ProcessInstanceApi = openapi_client.ProcessInstanceApi(api_client)

            try:
                response = api_instance.get_activity_instance_tree(**kwargs)
            except ApiException as e:
                logger.error(f'failed to get activity tree for process instance {kwargs}:\n{e}')
        return response

    @keyword("Get Process Instance Variable", tags=['process'])
    def get_process_instance_variable(self, process_instance_id: str, variable_name: str):
        """
        Returns the variable with the given name from the process instance with
        the given process_instance_id.

        Parameters:
            - ``process_instance_id``: ID of the target process instance
            - ``variable_name``: name of the variable to read

        == Example ==
        | ${variable} | Get Process Instance Variable |
        | ...         | process_instance_id=fcab43bc-b970-11eb-be75-0242ac110002 |
        | ...         | variable_name=foo |

        See also:
        https://docs.camunda.org/manual/7.5/reference/rest/process-instance/variables/get-single-variable/
        """
        with self._shared_resources.api_client as api_client:
            api_instance: ProcessInstanceApi = openapi_client.ProcessInstanceApi(api_client)

            try:
                response = api_instance.get_process_instance_variable(
                    id=process_instance_id, var_name=variable_name)
            except ApiException as e:
                logger.error(f'Failed to get variable {variable_name} from '
                             f'process instance {process_instance_id}:\n{e}')
        return response

    @keyword("Evaluate Decision", tags=['decision'])
    def evaluate_decision(self, key: str, variables: dict) -> list:
        """
        Evaluates a given decision and returns the result.
        The input values of the decision have to be supplied with `variables`.

        == Example ==
        | ${variables} | Create Dictionary | my_input=42 |
        | ${response} | Evaluate Decision | my_decision_table | ${variables} |
        """
        with self._shared_resources.api_client as api_client:
            api_instance = openapi_client.DecisionDefinitionApi(api_client)
            dto = CamundaResources.convert_dict_to_openapi_variables(variables)
            try:
                response = api_instance.evaluate_decision_by_key(
                    key=key,
                    evaluate_decision_dto=openapi_client.EvaluateDecisionDto(dto))
                return [CamundaResources.convert_openapi_variables_to_dict(r)
                        for r in response]
            except ApiException as e:
                logger.error(f'Failed to evaluate decision {key}:\n{e}')
