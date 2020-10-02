*** Settings ***
Library    Camunda.Execution
#Library    ../../../Camunda/Execution.py

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test starting process
    [Setup]    set camunda url    ${CAMUNDA_HOST}
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot

    # WHEN
    start process    ${process_definition_key}

Test starting process with variables
    [Setup]    set camunda url    ${CAMUNDA_HOST}
    #GIVEN
    ${process_definition_key}    Set Variable    demo_for_robot
    ${workload}    Create Dictionary    my_value=test1
    ${variables}    Create List    ${workload}

    # WHEN
    start process    ${process_definition_key}