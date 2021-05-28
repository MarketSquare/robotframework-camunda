*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}
Resource    ../cleanup.resource

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot
${TOPIC_NAME}    process_demo_element

*** Test Case ***
There shall be as many tasks as started processes
    [Documentation]    https://github.com/MarketSquare/robotframework-camunda/issues/6
    [Tags]    issue-6
    [Template]    Start processes and check amount of workloads
    1
    2
    4

There shall be as many tasks as started processes
    [Documentation]    https://github.com/MarketSquare/robotframework-camunda/issues/6
    [Tags]    issue-6
    [Template]    Start process with business key and check for particular workload
    1
    2
    4

*** Keywords ***
Start processes and check amount of workloads
    [Arguments]    ${n}
    Delete all instances from process '${PROCESS_DEFINITION_KEY}'
    FOR     ${i}    IN RANGE    0    ${n}
        start process     ${PROCESS_DEFINITION_KEY}
    END

    ${amount_of_workloads}    Get amount of workloads    ${TOPIC_NAME}
    Should be equal as integers    ${amount_of_workloads}    ${n}

Start process with business key and check for particular workload
    [Arguments]    ${n}
    Delete all instances from process '${PROCESS_DEFINITION_KEY}'
    FOR     ${i}    IN RANGE    0    ${n}
        ${last_process_instance}    start process     ${PROCESS_DEFINITION_KEY}    business_key=${i}
    END

    ${amount_of_workloads}    Get amount of workloads    ${TOPIC_NAME}    process_instance_id=${last_process_instance}[id]
    Should be equal as integers    ${amount_of_workloads}    1

