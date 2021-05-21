*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}


*** Variables ***
${CAMUNDA_HOST}              http://localhost:8080
${PROCESS_INSTANCE_ID}       ${EMPTY}
${ACTIVITY_INSTANCE_TREE}    ${EMPTY}


*** Test Cases ***
Get Process Definitions
    # Given
    Process Instance Is Present

    # When
    Camunda Is Requested For Activity Instances Of The Process Instance

    # Then
    Camunda Answered With An Activity Instance Tree


*** Keywords ***
Process Instance Is Present
    ${response}   Start Process    demo_for_robot
    Set Global Variable    ${PROCESS_INSTANCE_ID}    ${response}[id]

Camunda Is Requested For Activity Instances Of The Process Instance
    ${ACTIVITY_INSTANCE_TREE}    Get Activity Instance    id=${PROCESS_INSTANCE_ID}
    Set Global Variable    ${ACTIVITY_INSTANCE_TREE}

Camunda Answered With An Activity Instance Tree
    Should Not Be Empty    '${ACTIVITY_INSTANCE_TREE}'
