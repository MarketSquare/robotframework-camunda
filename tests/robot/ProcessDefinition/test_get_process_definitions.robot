*** Settings ***
Library    CamundaLibrary
Suite Setup    Set Camunda Configuration    ${configuration}

*** Variables ***
${CAMUNDA_HOST}           http://localhost:8080
${PROCESS_DEFINITIONS}    ${EMPTY}


*** Test Cases ***
Get All Process Definitions
    # Given
    At Least One Process Definition Is Present

    # When
    Camunda Is Requested For All Existing Process Definitions

    # Then
    Camunda Answered With A List Of At Least One Process Definition


*** Keywords ***
At Least One Process Definition Is Present
    Deploy    ${CURDIR}/../../bpmn/demo_for_robot.bpmn

Camunda Is Requested For All Existing Process Definitions
    ${PROCESS_DEFINITIONS}    Get Process Definitions
    Log    ${PROCESS_DEFINITIONS}
    Set Global Variable    ${PROCESS_DEFINITIONS}

Camunda Answered With A List Of At Least One Process Definition
    Should Be True    len($PROCESS_DEFINITIONS) > 1
    ...    msg=No Process Definitions found.
