*** Settings ***
Library    CamundaLibrary.ProcessDefinition
Library    CamundaLibrary.ProcessInstance
Library    CamundaLibrary.ExternalTask
Library    Collections


*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test starting process
    [Setup]    Init Camunda Host
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot

    # WHEN
    ${process_instance}    start process    ${process_definition_key}

    [Teardown]    delete process instance    ${process_instance}[id]

Test starting process with variables
    [Setup]    Init Camunda Host
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot
    ${existing_topic}    Set Variable    process_demo_element

    ${variable1_value}    Set Variable    test1
    ${variable1_value_object}    Create Dictionary    value=${variable1_value}    type=String
    ${variable1_key}    Set Variable    my_value
    ${variables}    Create Dictionary    ${variable1_key}=${variable1_value_object}

    # WHEN
    start process    ${process_definition_key}   ${variables}

    # AND
    ${workload}     fetch and lock workloads   topic=${existing_topic}

    # THEN
    Should Not be empty    ${workload}

    # AND
    ${first_workload}    Set Variable    ${workload}[0]
    dictionary should contain key    ${first_workload}    ${variable1_key}
    Should Not be empty    ${first_workload}[${variable1_key}]
    dictionary should contain key    ${first_workload}[${variable1_key}]    value
    Should Not be empty    ${first_workload}[${variable1_key}][value]
    Should Be Equal    ${variable1_value}    ${first_workload}[${variable1_key}][value]
    [Teardown]    complete task   ${existing_topic}

*** Keywords ***
Init Camunda Host
    CamundaLibrary.ProcessDefinition.set camunda url    ${CAMUNDA_HOST}
    CamundaLibrary.ProcessInstance.set camunda url    ${CAMUNDA_HOST}
    CamundaLibrary.ExternalTask.set camunda url    ${CAMUNDA_HOST}