*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}
Resource    ../cleanup.resource
Test Setup    Delete all instances from process '${PROCESS_DEFINITION_KEY}'

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot
${EXISTING_TOPIC}    process_demo_element

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test 'Notify failure' for existing topic
    # GIVEN
    Start process    ${PROCESS_DEFINITION_KEY}
    ${variables}    Create Dictionary    text=Manna Manna

    # AND
    ${work_items}    fetch workload   topic=${existing_topic}

    # WHEN
    notify failure

    # THEN
    ${workload}    Fetch Workload    topic=${existing_topic}
    Should Be Empty    ${workload}