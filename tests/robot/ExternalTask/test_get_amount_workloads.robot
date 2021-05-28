*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_URL}
Resource    ../cleanup.resource
Test Setup    Delete all instances from process '${PROCESS_DEFINITION_KEY}'

*** Variables ***
${CAMUNDA_URL}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot
${TOPIC_NAME}    process_demo_element

*** Test Case ***
There shall be as many tasks as started processes
    [Template]    Start processes and check amount of workloads
    1
    2
    4

There shall be as many tasks as started processes
    [Template]    Start process with business key and check for particular workload
    1
    2
    4

*** Keywords ***
Start processes and check amount of workloads
    [Arguments]    ${n}
    FOR     ${i}    IN RANGE    0    ${n}
        start process     ${PROCESS_DEFINITION_KEY}
    END

    ${amount_of_workloads}    Get amount of workloads    ${TOPIC_NAME}
    Should be equals as integers    ${amount_of_workloads}    ${n}

Start process with business key and check for particular workload
    [Arguments]    ${n}
    FOR     ${i}    IN RANGE    0    ${n}
        start process     ${PROCESS_DEFINITION_KEY}    ${i}
    END

    ${amount_of_workloads}    Get amount of workloads    ${TOPIC_NAME}    ${business_key}=${n}
    Should be equals as integers    ${amount_of_workloads}    0

    ${amount_of_workloads}    Get amount of workloads    ${TOPIC_NAME}    ${business_key}=1
    Should be equals as integers    ${amount_of_workloads}    1

