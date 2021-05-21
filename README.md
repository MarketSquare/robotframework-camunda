# Robot Framework Camunda

This library provides keywords for accessing camunda workflow engine. Complete REST API reference of camunda 
can be found [here](https://docs.camunda.org/manual/7.14/reference/rest/).

**Please review [issue board](https://github.com/MarketSquare/robotframework-camunda/issues) for 
known issues or report one yourself. You are invited to contribute pull requests.**

## Documentation

Keyword documentation is provided [here](https://postadress.gitlab.io/robotframework/robotframework-camunda-mirror/latest/keywords/camundalibrary/)

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

*** Test Cases ***
Test deployment of models
    ${response}    deploy model from file    ${CURDIR}/../../bpmn/demo_for_robot.bpmn
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