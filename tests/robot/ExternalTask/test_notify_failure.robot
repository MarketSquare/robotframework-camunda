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
Test 'Notify failure' for existing topic
    Given A new process instance
    ${process_instance}    And process instance fetched

    When notify failure   retry_timeout=${None}

    Then No Process Instance available at topic    topic=${existing_topic}    error_message=Notifying Failure failed. Process instance should not be available anymore at service task.
    And Process instance is incident    ${process_instance}

Test 'Notify failure' with setting retry_timeout
    # GIVEN
    Given A new process instance
    ${process_instance}    And process instance fetched

    When notify failure    retry_timeout=100

    Then No Process Instance available at topic    topic=${existing_topic}    error_message=Notifying Failure failed. Process instance should not be available anymore at service task.
    And Process instance is incident    ${process_instance}

Test 'Notify failure' with unfinished retries
    Given A new process instance
    ${process_instance}    And Fetch Workload and notify failure    retries=1    retry_timeout=0

    Then Process Instance available at topic    topic=${existing_topic}    error_message=Notifying Failure failed. Process instance should not be available anymore at service task.
    And Process instance is not incident    ${process_instance}

Test 'Notify failure' with retries countdown
    Given A new process instance
    ${process_instance}    And Fetch Workload and notify failure    retries=1    retry_timeout=0

    ${process_instance_retry}    When Fetch Workload and notify failure    retries=1    retry_timeout=0

    Then No Process Instance available at topic    topic=${existing_topic}    error_message=Notifying Failure failed. Process instance should not be available anymore at service task.
    And Process instance is incident    ${process_instance_retry}

*** Keywords ***
A new process instance
    Start process    ${PROCESS_DEFINITION_KEY}
    ${variables}    Create Dictionary    text=Manna Manna

process instance fetched
    fetch workload   topic=${existing_topic}        lock_duration=500
    ${process_instance}    Get fetch response
    log    ${process_instance}
    Should Not be Empty    ${process_instance}    Failure while setting up test case. No process instance available to send failure for.
    [Return]    ${process_instance}

Fetch Workload and notify failure
    [Arguments]    ${retries}=0    ${retry_timeout}=100
    ${process_instance}    process instance fetched
    notify failure    retries=${retries}    retry_timeout=${retry_timeout}
    [Return]    ${process_instance}

No Process Instance available at topic
    [Arguments]    ${topic}    ${error_message}=None
    Sleep    1 s
    ${process_instance}    Get process instance for topic    ${topic}
    Should Be Empty    ${process_instance}    ${error_message}
    [Return]    ${process_instance}

Process Instance available at topic
    [Arguments]    ${topic}    ${error_message}=None
    Sleep    500 ms
    ${process_instance}    Get process instance for topic    ${topic}
    Should Not Be Empty    ${process_instance}    ${error_message}
    [Return]    ${process_instance}

Get process instance for topic
    [Arguments]    ${topic}
    Fetch Workload    topic=${topic}
    ${process_instance}    Get fetch response
    [Return]    ${process_instance}

Process instance is incident
    [Arguments]    ${process_instance}
    ${process_instance_after_failure}    Get process instances    process_instance_ids=${process_instance}[process_instance_id]
    log    ${process_instance_after_failure}
    Should Not Be Empty    ${process_instance_after_failure}    Notifying Failure failed. Process instance is instance but should be an incident.

    ${incident}    Get incidents    process_instance_id=${process_instance}[process_instance_id]
    log    ${incident}
    Should Not be Empty    ${incident}     Getting incident failed. There is no incident availabe matching the process instance.

Process instance is not incident
    [Arguments]    ${process_instance}
    ${incident}    Get incidents    process_instance_id=${process_instance}[process_instance_id]
    log    ${incident}
    Should be Empty    ${incident}     Getting incident failed. There is no incident availabe matching the process instance.