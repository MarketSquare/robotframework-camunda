# Robot Framework Camunda

This library provides keywords for accessing camunda workflow engine. Complete REST API reference of camunda 
can be found [here](https://docs.camunda.org/manual/7.5/reference/rest/).

**Library is in an early stage. Please review [issue board](https://gitlab.com/postadress/robotframework/robotframework-camunda/-/issues) for known issues or report one yourself. You are 
invited to contribute pull requests.**

## Documentation
Keyword documentation exists for sub-libraries:
- [Deployment](https://postadress.gitlab.io/robotframework/robotframework-camunda/keywords/deployment/)
- [ProcessInstance](https://postadress.gitlab.io/robotframework/robotframework-camunda/keywords/processinstance/)
- [ProcessDefinition](https://postadress.gitlab.io/robotframework/robotframework-camunda/keywords/processdefinition/)
- [ExternalTask](https://postadress.gitlab.io/robotframework/robotframework-camunda/keywords/externaltask/)

## Installation
The library is published on [pypi.org](https://pypi.org/project/robotframework-camunda/) and can be installed with pip:
```
pip install robotframework-camunda
```

## Running robotframework-camunda
The `tests` folder has example robot tests for keywords already implemented. Those tests assume you already have an 
instance of camunda running.

### Deploy process definition
```robot
*** Settings ***
Library    Camunda.Deployment    ${CAMUNDA_HOST}

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test deployment of models
    ${response}    deploy model from file    ${CURDIR}/../../bpmn/demo_for_robot.bpmn
```

### Starting a process instance
```robot
*** Settings ***
Library    Camunda.ProcessDefinition    ${CAMUNDA_HOST}

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
"Executing task" bascially means, you execute a robot task that *fetches* a workload from camunda, processes it and 
returns its workload back to camunda during *completion*. Main keywords involved are:
1. `Camunda.ExternalTask.Fetch and lock workloads`
1. `Camunda.ExternalTask.Complete Task`

```robot
*** Settings ***
Library    Camunda.ExternalTask    ${CAMUNDA_HOST}
Library    Collections

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8000
${existing_topic}    process_demo_element

*** Test Cases ***
Test 'fetch and lock' for non existing topic
    # WHEN
    ${work_items}    fetch and lock workloads   topic=${existing_topic}

    # THEN
    Should Not Be Empty    ${work_items}

    ${recent_task}    Get recent process instance
    log    Recent task:\t${recent_task}

    ${my_result}    Create Dictionary    lastname=Stahl
    complete task   ${existing_topic}    ${recent_task}    ${my_result}
```