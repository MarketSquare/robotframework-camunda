*** Settings ***
Library    CamundaLibrary
Suite Setup    Set Camunda Configuration    ${configuration}
Suite Teardown    Clean Up Process Instance


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
    ${activity_instances}    Set Variable    ${ACTIVITY_INSTANCE_TREE}[child_activity_instances]
    Length Should Be    ${activity_instances}    1
    Should Be Equal    Activity_process_element    ${activity_instances}[0][activity_id]

Clean Up Process Instance
    Run Keyword If    $PROCESS_INSTANCE_ID
    ...    Delete Process Instance    ${PROCESS_INSTANCE_ID}
