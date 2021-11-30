*** Settings ***
Library    CamundaLibrary
Resource    ../cleanup.resource
Suite Setup    Set Camunda Configuration    ${configuration}
Test Setup    Delete all instances from process '${PROCESS_DEFINITION_KEY}'

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot
${EXISTING_TOPIC}    process_demo_element

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
BPMN error without task does not fail
    # only throws a warning
    throw bpmn error    de1

Test 'throw bpmn error' for existing topic
    [Setup]    set camunda url    ${CAMUNDA_HOST}
    # GIVEN
    Start process    ${PROCESS_DEFINITION_KEY}
    ${variables}    Create Dictionary    text=Manna Manna

    # AND
    ${work_items}    fetch workload   topic=${existing_topic}

    # WHEN
    throw bpmn error    de1    Alles kaputt    variables=${variables}

    # THEN
    ${workload}    Fetch Workload    handle_error
    Should Not Be Empty    ${workload}

    Should Be Equal As Strings    Manna Manna    ${workload}[text]
    Should Be Equal As Strings    de1    ${workload}[error_code]
    Should Be Equal As Strings    Alles kaputt    ${workload}[error_message]
