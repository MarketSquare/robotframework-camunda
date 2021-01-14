*** Settings ***
Library    CamundaLibrary.ProcessDefinition    ${CAMUNDA_HOST}
Library    CamundaLibrary.ProcessInstance
Library    CamundaLibrary.ExternalTask
Library    Collections


*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test starting process
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot

    # WHEN
    ${process_instance}    start process    ${process_definition_key}

    [Teardown]    delete process instance    ${process_instance}[id]

Test starting process with variables
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot
    ${existing_topic}    Set Variable    process_demo_element

    ${variable1_value}    Set Variable    test1
    ${variable1_key}    Set Variable    my_value
    ${variables}    Create Dictionary    ${variable1_key}=${variable1_value}

    # WHEN
    start process    ${process_definition_key}   ${variables}

    # AND
    ${first_workload}     fetch and lock workloads   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    ${variable1_key}
    Should Not be empty    ${first_workload}[${variable1_key}]
    Should Be Equal    ${variable1_value}    ${first_workload}[${variable1_key}]
    [Teardown]    complete task

Test starting process with dict variables
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot
    ${existing_topic}    Set Variable    process_demo_element

    ${variable1_value}    Set Variable    test1
    ${variable1_key}    Set Variable    my_value
    ${variables1}    Create Dictionary    ${variable1_key}=${variable1_value}
    ${variables}    Create Dictionary    variables1=${variables1}

    # WHEN
    start process    ${process_definition_key}   ${variables}

    # AND
    ${first_workload}     fetch and lock workloads   topic=${existing_topic}

    # THEN
    Should Not be empty    ${first_workload}

    # AND
    dictionary should contain key    ${first_workload}    variables1
    dictionary should contain key    ${first_workload}[variables1]    ${variable1_key}
    Should Not be empty    ${first_workload}[variables1][${variable1_key}]
    Should Be Equal    ${variable1_value}    ${first_workload}[variables1][${variable1_key}]
    [Teardown]    complete task
