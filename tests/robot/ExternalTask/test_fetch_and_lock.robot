*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}    ${configuration}
Library    Collections
Resource    ../cleanup.resource
Test Setup    Delete all instances from process '${PROCESS_DEFINITION_KEY}'
Test Teardown    Reset CamundaLibrary

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${PROCESS_DEFINITION_KEY}    demo_for_robot
${EXISTING_TOPIC}    process_demo_element

*** Test Cases ***
Test 'fetch and lock' for existing topic
    #GIVEN
    start process    ${PROCESS_DEFINITION_KEY}    ${{{'variable_1': 1}}}
    #WHEN
    ${variables}    fetch workload    ${EXISTING_TOPIC}
    #THEN
    Should Not Be Empty    ${variables}    Fetching failed. Expected workload at topic '${EXISTING_TOPIC}'
    #AND
    Dictionary should contain key    ${variables}    variable_1

Test 'fetch and lock' with only specific variables
    #GIVEN
    ${variable_name1}    Set Variable    variable1
    ${variable_name2}    Set Variable    variable2
    ${input_variables}    Create Dictionary
    ...    ${variable_name1}=1
    ...    ${variable_name2}=2
    start process   ${PROCESS_DEFINITION_KEY}    ${input_variables}

    #WHEN
    ${variables}    fetch workload    ${EXISTING_TOPIC}    variables=${{['${variable_name1}']}}

    #THEN
    Dictionary Should Contain key    ${variables}    ${variable_name1}
    Dictionary Should Not Contain Key    ${variables}    ${variable_name2}

Test 'fetch and lock' for non existing topic
    # GIVEN
    ${non_existing_topic}    Set Variable    asdqeweasdwe

    # WHEN
    ${work_items}    fetch workload   topic=${non_existing_topic}

    # THEN
    Should Be Empty    ${work_items}

Test 'fetch and lock' for inacurrate camunda url
    # GIVEN
    ${invalid_camunda_url}    Set Variable    https://localhost:9212
    set camunda url    ${invalid_camunda_url}

    # WHEN
    ${pass_message}    ${error}    Run Keyword and ignore error    fetch workload    topic=random

    # THEN
    Should Be Equal    FAIL    ${pass_message}
    Should contain    ${error}    ConnectionError

*** Keywords ***
Reset CamundaLibrary
    set camunda url    ${CAMUNDA_HOST}
    complete task