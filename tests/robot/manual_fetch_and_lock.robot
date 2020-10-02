*** Settings ***
Library    Camunda.ExternalTask
Library    Collections

*** Test Cases ***
Test 'fetch and lock' for non existing topic
    [Setup]    set camunda url    http://localhost:8080/engine-rest
    # GIVEN
    ${existing_topic}    Set Variable    process_demo_element

    # WHEN
    ${work_items}    fetch and lock workloads   topic=${existing_topic}

    # THEN
    Should Not Be Empty    ${work_items}

    ${recent_task}    get recent task id
    log    Recent task:\t${recent_task}

    ${my_result}    Create Dictionary    lastname=Stahl
    complete task   ${existing_topic}    ${recent_task}    ${my_result}
