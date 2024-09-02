[![PyPI status](https://img.shields.io/pypi/status/robotframework-camunda.svg)](https://pypi.python.org/pypi/robotframework-camunda/) [![pipeline status](https://gitlab.com/robotframework-camunda-demos/robotframework-camunda-mirror/badges/master/pipeline.svg)](https://gitlab.com/robotframework-camunda-demos/robotframework-camunda-mirror/-/commits/master) [![PyPi license](https://badgen.net/pypi/license/robotframework-camunda/)](https://pypi.com/project/robotframework-camunda/) [![PyPi version](https://badgen.net/pypi/v/robotframework-camunda/)](https://pypi.org/project/robotframework-camunda) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/robotframework-camunda.svg)](https://pypi.python.org/pypi/robotframework-camunda/) [![PyPI download month](https://img.shields.io/pypi/dm/robotframework-camunda.svg)](https://pypi.python.org/pypi/robotframework-camunda/) 

# Camunda 7 vs Camunda 8
Since it requested from time o time: No, this library won't support Camunda 8. C8 and it's API are completely different and C8 API has had backwards incompatible changes due to its relatively low maturity. This library supports to when:
- You migrate to Camunda 7 based workflow engine and you want to validate your processes are still working.

If you need to test C8, it is recommended to build a separate library. This had been the initial idea behind [Robot Framework Zeebe library](https://github.com/MarketSquare/robotframework-zeebe) which is looking for a maintainer.

# Robot Framework Camunda

This library provides keywords for accessing camunda workflow engine. Complete REST API reference of camunda 
can be found [here](https://docs.camunda.org/manual/7.14/reference/rest/).

**Please review [issue board](https://github.com/MarketSquare/robotframework-camunda/issues) for 
known issues or report one yourself. You are invited to contribute pull requests.**

| Supported | Tested |
| :----- | :----- |
| Python >= 3.8 | 3.8, 3.9, 3.10, 3.11, 3.12 |
| Camunda 7 >= 7.14 | 7.14, 7.15, 7.16, 7.17, 7.18, 7.19, 7.20 |

## Documentation

Keyword documentation is provided [here](https://robotframework-camunda-demos.gitlab.io/robotframework-camunda-mirror/latest/keywords/camundalibrary)

## Installation

The library is published on [pypi.org](https://pypi.org/project/robotframework-camunda/) and can be installed with pip:

```shell
pip install robotframework-camunda
```

## Running robotframework-camunda
The `tests` folder has example robot tests for keywords already implemented. Those tests assume you already have an 
instance of camunda running.

Easiest way of running camunda is to launch with with docker:
```shell
docker run -d --name camunda -p 8080:8080 camunda/camunda-bpm-platform:run-latest
```

### Deploy process definition

```robot
*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${MODEL_FOLDER}    ${CURDIR}/../models

*** Test Cases ***
Test deployment of a single model in 1 deployment
    ${response}    deploy    ${MODEL_FOLDER}/demo_for_robot.bpmn

Test deployment of several models in 1 deployment
    ${response}    deploy    ${MODEL_FOLDER}/demo_for_robot.bpmn    ${MODEL_FOLDER}/demo_embedded_form.html
```

### Starting a process instance

```robot
*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test starting process
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot

    # WHEN
    ${process_instance}    start process    ${process_definition_key}
```

### Execute Task
"Executing task" bascialy means, you execute a robot task that *fetches* a workload from camunda, processes it and 
returns its workload back to camunda during *completion*. Main keywords involved are:
1. `CamundaLibrary.Fetch workload`
1. `CamundaLibrary.Complete Task`

```robot
*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}
Library    Collections

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8000
${existing_topic}    process_demo_element

*** Test Cases ***
Process workload
    ${variables}    fetch workload   topic=${existing_topic}
    ${recent_task}    Get fetch response
    log    Recent task:\t${recent_task}

    Pass Execution If    not ${recent_task}    No workload fetched from Camunda
 
    # do some processing
    
    # create result and return workload to Camunda
    ${my_result}    Create Dictionary    lastname=Stahl
    complete task   ${my_result}
```

### Authentication

**Prerequisite: CamundaLibrary >= 2.0**

If your Camunda Platform REST API requires authentication (it should at least in production!) then you do not need to pass the host url to CamundaLibrary during intialization. You require the `Set Camunda Configuration` keyword. The keyword expects a dictionary with host url and (optional) either username with password or api key with optional api key prefix. See the following example.

```robot
*** Settings ***
Library    CamundaLibrary


*** Test Cases ***
Demonstrate basic auth
    ${camunda_config}    Create Dictionary    host=http://localhost:8080    username=markus    password=%{ENV_PASSWORD}
    Set Camunda Configuration    ${camunda_config}
    ${deployments}    Get deployments    #uses basic auth now implictly

Demonstrate Api Key
    ${camunda_config}    Create Dictionary    host=http://localhost:8080    api_key=%{ENV_API_KEY}   api_key_prefix=Bearer
    Set Camunda Configuration    ${camunda_config}
    ${deployments}    Get deployments    #uses api key implicitly
```
If you would pass in username+password *and* and API key, the API key will always be chosen over the username+password. So better leave it out for not confusing everybody.
