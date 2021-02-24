*** Settings ***
Library    CamundaLibrary
Library    Collections

*** Test Cases ***
Test 'fetch and lock' for non existing topic
    [Setup]    set camunda url    http://localhost:8080
    # GIVEN
    ${existing_topic}    Set Variable    process_demo_element

    # WHEN
    ${work_items}    fetch workload   topic=${existing_topic}

    # THEN
    #Should Not Be Empty    ${work_items}

    ${recent_task}    Get recent process instance
    log    Recent task:\t${recent_task}

    ${my_result}    Create Dictionary    lastname=Stahl
    complete task   ${my_result}
