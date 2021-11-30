*** Settings ***
Library    CamundaLibrary    ${CAMUNDA_HOST}    ${configuration}
Suite Setup    Set Camunda Configuration    ${configuration}

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080

*** Test Cases ***
Test unlock without having fetched anything
    unlock

Test 'fetch and lock' for non existing topic
    [Setup]    set camunda url    ${CAMUNDA_HOST}
    # GIVEN
    ${non_existing_topic}    Set Variable    asdqeweasdwe

    # AND
    ${work_items}    fetch workload   topic=${non_existing_topic}

    # EXPECTED
    Should Be Empty    ${work_items}

    # WHEN
    unlock