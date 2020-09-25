*** Settings ***
Library    ../../Camunda/ExternalTask/ExternalTask.py

*** Test Cases ***
Test 'fetch and lock' for non existing topic
    [Setup]    set camunda url    http://localhost:8080/engine-rest
    # GIVEN
    ${non_existing_topic}    Set Variable    asdqeweasdwe

    # WHEN
    ${work_items}    fetch and lock workloads   topic=${non_existing_topic}

    # THEN
    Should Be Empty    ${work_items}

Test 'fetch and lock' for inacurrate camunda url
    # GIVEN
    ${invalid_camunda_url}    Set Variable    https://localhost:9212
    set camunda url    ${invalid_camunda_url}

    # WHEN
    ${pass_message}    ${error}    Run Keyword and ignore error    fetch and lock workloads    topic=random

    # THEN
    Should Be Equal    FAIL    ${pass_message}
    Should contain    ${error}    ConnectionError


